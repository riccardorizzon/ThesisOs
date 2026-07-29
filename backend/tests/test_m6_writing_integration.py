"""M6.5 Writing Qualification — writer route + chapter persistence integration.

Writer route exercised through the orchestrated graph with the Event Bus attached
(grounded draft + citations, degraded paths), and the draft → chapter persistence
flow exercised through ChapterService (the workspace save path).
"""

from __future__ import annotations

import pytest
from langgraph.checkpoint.memory import InMemorySaver

from app.graph.conversation import build_graph
from app.graph.orchestration.constants import WRITER_ROUTE
from app.llm.base import TokenChunk
from app.runtime.events import EventType
from app.schemas.chapter import ChapterContentUpdate, ChapterCreate
from app.schemas.graph_state import GraphState, Message
from app.schemas.memory import PromptContext
from app.schemas.retrieval import SearchResultItem
from app.schemas.run_context import RunContext
from app.services.chapter import ChapterService
from tests.support.orchestration_llm import OrchestrationLLM

WRITER_MSG = "Write the chapter on craftsmanship"


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


class WriterFailLLM(OrchestrationLLM):
    """Routes to writer (generate) but fails when drafting (astream)."""

    async def astream(self, messages, *, model=None, params=None):
        raise RuntimeError("vertex down")
        yield TokenChunk(text="")  # pragma: no cover — makes this an async generator


def _result():
    return SearchResultItem(
        chunk_id="c1", document_id="d1", chunk_hash="h1", score=0.9,
        content="Craft is the disciplined pursuit of quality.", document_title="Doc",
    )


async def _run(llm, *, retrieval, emitter, message=WRITER_MSG):
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
    final = None
    async for state in graph.astream(
        GraphState(messages=[Message(role="user", content=message)]), cfg, stream_mode="values"
    ):
        final = state
    return final


def _completed(emitter):
    return {e.metadata.get("agent") for e in emitter.events if e.event_type == EventType.NODE_COMPLETED}


def _route(emitter):
    routes = [e.metadata.get("route") for e in emitter.events if e.event_type == EventType.ROUTE_SELECTED]
    return routes[0] if routes else None


# --- writer route through the orchestrated graph + Event Bus ---------------

@pytest.mark.asyncio
async def test_writer_route_drafts_grounded_with_citations():
    spy, emitter = SpyRetrieval([_result()]), SpyEmitter()
    final = await _run(
        OrchestrationLLM(route=WRITER_ROUTE, stream_parts=["Craftsmanship ", "matters."]),
        retrieval=spy, emitter=emitter,
    )
    assert _route(emitter) == WRITER_ROUTE
    # Primary query search + Sennett author-doc boost ("craftsmanship" in corpus_query).
    assert spy.search_calls == 2
    assert "writer" in _completed(emitter)
    assert "conversation" not in _completed(emitter)  # writer terminates the turn
    assert final.get("draft") == "Craftsmanship matters."
    assert [c.source_id for c in final.get("citations", [])] == ["d1"]


@pytest.mark.asyncio
async def test_writer_empty_context_still_drafts_no_citations():
    spy, emitter = SpyRetrieval([]), SpyEmitter()
    final = await _run(
        OrchestrationLLM(route=WRITER_ROUTE, stream_parts=["Best-effort draft."]),
        retrieval=spy, emitter=emitter,
    )
    assert final.get("draft") == "Best-effort draft."
    assert final.get("citations", []) == []
    assert any(e.message == "empty_context" for e in final.get("errors", []))


@pytest.mark.asyncio
async def test_writer_generation_failed_finalizes_turn():
    spy, emitter = SpyRetrieval([_result()]), SpyEmitter()
    final = await _run(WriterFailLLM(route=WRITER_ROUTE), retrieval=spy, emitter=emitter)
    # Continue-degraded (ADR-0031 §7): the writer catches the failure and returns
    # `generation_failed` in errors — the node completes (not NodeFailed) and the
    # turn finalizes with no draft.
    assert "writer" in _completed(emitter)
    assert not final.get("draft")
    assert any(e.message == "generation_failed" for e in final.get("errors", []))


# --- draft → chapter persistence (workspace save flow) ---------------------

@pytest.mark.asyncio
async def test_draft_persists_as_versioned_chapter(db_session):
    svc = ChapterService()
    chapter = await svc.create(ChapterCreate(title="Craftsmanship"), session=db_session)
    await db_session.commit()

    draft = "Craftsmanship matters because quality compounds over time."
    saved = await svc.update_content(
        chapter.id, ChapterContentUpdate(content_md=draft, expected_version=chapter.version),
        session=db_session,
    )
    await db_session.commit()

    assert saved.version == 2
    assert saved.content_md == draft
    reread = await svc.get(chapter.id, session=db_session)
    assert reread.content_md == draft
    history = await svc.list_versions(chapter.id, session=db_session)
    assert [(v.version, v.change_kind) for v in history] == [(1, "WRITE"), (2, "EDIT")]
