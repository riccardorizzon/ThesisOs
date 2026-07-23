"""M5.5 Runtime Qualification — orchestrated runtime integration.

Error contracts exercised through the real ConversationService turn lifecycle
(degraded orchestration still replies), and both routes exercised through the
orchestrated graph with the Event Bus attached.
"""

from __future__ import annotations

import json

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from sqlalchemy import select

from app.db import models
from app.graph.conversation import build_graph
from app.graph.orchestration.constants import DEFAULT_ROUTE, GROUNDED_ROUTE
from app.llm.base import TokenChunk
from app.runtime.events import EventType
from app.schemas.graph_state import GraphState, Message
from app.schemas.memory import PromptContext
from app.schemas.retrieval import SearchResultItem
from app.schemas.run_context import RunContext
from app.services.conversation.service import ConversationService
from tests.support.orchestration_llm import OrchestrationLLM

VALID_SUPERVISOR = json.dumps({"plan_steps": ["Respond"], "route_hint": "conversation", "no_objective": False})
VALID_PLANNER = json.dumps({"plan_steps": ["Respond"], "task_title": "Chat turn", "unplannable": False})
VALID_ROUTER = json.dumps({"route": "conversation"})


class ConfigurableLLM:
    """Per-agent JSON control so each degraded contract path can be triggered."""

    def __init__(self, *, supervisor: str, planner: str, router: str, stream_parts=("reply",)) -> None:
        self._by_agent = {"Supervisor agent": supervisor, "Planner agent": planner, "Router agent": router}
        self.stream_parts = list(stream_parts)

    async def generate(self, messages, *, model=None, params=None) -> str:
        system = messages[0]["content"] if messages else ""
        for marker, payload in self._by_agent.items():
            if marker in system:
                return payload
        return "{}"

    async def astream(self, messages, *, model=None, params=None):
        for part in self.stream_parts:
            yield TokenChunk(text=part)
        yield TokenChunk(text="", finish_reason="stop", metadata={"usage": {"total_tokens": 1}})

    async def embed(self, *a, **k):
        raise NotImplementedError

    async def vision(self, *a, **k):
        raise NotImplementedError


class _StubMemory:
    async def load_prompt_context(self, **kwargs):
        return PromptContext()


class SpyRetrieval:
    def __init__(self, results=None) -> None:
        self._results = results or []
        self.search_calls = 0

    async def search(self, query, *, filters=None, limit=10, hybrid_alpha=0.5, session=None):
        self.search_calls += 1
        return self._results, "fake-model"


class SpyEmitter:
    def __init__(self) -> None:
        self.events = []

    async def emit(self, event) -> None:
        self.events.append(event)


@pytest.fixture
async def langgraph_ready(db_session):
    from app.graph.checkpointer import ensure_langgraph_schema

    await ensure_langgraph_schema()


async def _collect(svc: ConversationService) -> list[dict]:
    return [e async for e in svc.stream_turn(conversation_id=None, user_text="hello")]


# --- Error contracts: degraded orchestration still replies (through the service) ---

@pytest.mark.parametrize(
    "supervisor,planner,router,label",
    [
        (json.dumps({"no_objective": True}), VALID_PLANNER, VALID_ROUTER, "no_objective"),
        (VALID_SUPERVISOR, json.dumps({"unplannable": True}), VALID_ROUTER, "unplannable"),
        (VALID_SUPERVISOR, VALID_PLANNER, "{}", "no_route"),
    ],
)
@pytest.mark.asyncio
async def test_degraded_orchestration_still_replies(
    db_session, langgraph_ready, monkeypatch, supervisor, planner, router, label
):
    llm = ConfigurableLLM(supervisor=supervisor, planner=planner, router=router, stream_parts=["reply"])
    monkeypatch.setattr("app.services.conversation.service.get_llm_client", lambda: llm)
    monkeypatch.setattr(
        "app.services.conversation.service.get_orchestration_llm_client",
        lambda: llm,
    )

    events = await _collect(ConversationService())

    assert any(e["event"] == "token" for e in events), f"{label}: no token"
    assert any(e["event"] == "done" for e in events), f"{label}: no done"
    assert not any(e["event"] == "error" for e in events), f"{label}: unexpected error"


@pytest.mark.asyncio
async def test_agent_run_graph_name_is_orchestrated(db_session, langgraph_ready, monkeypatch):
    llm = OrchestrationLLM(stream_parts=["hi"])
    monkeypatch.setattr("app.services.conversation.service.get_llm_client", lambda: llm)
    monkeypatch.setattr(
        "app.services.conversation.service.get_orchestration_llm_client",
        lambda: llm,
    )
    await _collect(ConversationService())

    db_session.expire_all()
    run = (
        await db_session.execute(select(models.AgentRun).order_by(models.AgentRun.created_at.desc()).limit(1))
    ).scalar_one()
    assert run.graph == "orchestrated_conversation"
    assert run.status == "done"


# --- Both routes through the orchestrated graph + Event Bus (deterministic, no DB) ---

async def _run_graph(llm, *, retrieval: SpyRetrieval, emitter: SpyEmitter) -> list[dict]:
    rc = RunContext(conversation_id="c", agent_run_id="r", trace_id="t", request_id="q")
    graph = build_graph(
        llm,
        checkpointer=InMemorySaver(),
        memory_service=_StubMemory(),
        retrieval_service=retrieval,
        emitter=emitter,
        run_context=rc,
    )
    cfg = {"configurable": {"thread_id": "c", "run_context": rc.model_dump()}}
    return [
        chunk
        async for chunk in graph.astream(
            GraphState(messages=[Message(role="user", content="hello")]), cfg, stream_mode="custom"
        )
    ]


def _completed_agents(emitter: SpyEmitter) -> set[str]:
    return {e.metadata.get("agent") for e in emitter.events if e.event_type == EventType.NODE_COMPLETED}


def _selected_route(emitter: SpyEmitter) -> str | None:
    routes = [e.metadata.get("route") for e in emitter.events if e.event_type == EventType.ROUTE_SELECTED]
    return routes[0] if routes else None


@pytest.mark.asyncio
async def test_conversation_route_skips_retriever():
    spy_ret, emitter = SpyRetrieval(), SpyEmitter()
    chunks = await _run_graph(OrchestrationLLM(route=DEFAULT_ROUTE, stream_parts=["hi"]), retrieval=spy_ret, emitter=emitter)

    assert spy_ret.search_calls == 0
    assert any(c.get("type") == "token" for c in chunks)
    assert _selected_route(emitter) == DEFAULT_ROUTE
    assert "retriever" not in _completed_agents(emitter)


@pytest.mark.asyncio
async def test_grounded_route_runs_retriever_and_streams_sources():
    item = SearchResultItem(
        chunk_id="c1", document_id="d1", chunk_hash="h1", score=0.9, content="Evidence.", document_title="Doc"
    )
    spy_ret, emitter = SpyRetrieval([item]), SpyEmitter()
    chunks = await _run_graph(OrchestrationLLM(route=GROUNDED_ROUTE, stream_parts=["grounded"]), retrieval=spy_ret, emitter=emitter)

    assert spy_ret.search_calls == 1
    assert any(c.get("type") == "sources" for c in chunks)
    assert _selected_route(emitter) == GROUNDED_ROUTE
    assert "retriever" in _completed_agents(emitter)
