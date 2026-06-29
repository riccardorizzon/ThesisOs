"""M6.5 writing eval harness — deterministic routing KPI + citation discipline.

Routing: feeds the router node a raw LLM route per case and asserts the final
wired dispatch key (writer activation on drafting intent). Citation: the writer
node only emits citations for retrieved sources (ADR-0031 §5).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.graph.router import make_router_node
from app.graph.routing import route_after_router
from app.graph.writer import LLMWriter, make_writer_node
from app.llm.base import TokenChunk
from app.schemas.graph_state import GraphState, Message, RetrievedChunk

_FIXTURE = Path(__file__).parent / "fixtures" / "m6_writing_eval.json"


class RouteLLM:
    def __init__(self, payload: str) -> None:
        self._payload = payload

    async def generate(self, messages, *, model=None, params=None) -> str:
        return self._payload

    async def astream(self, *a, **k):
        raise NotImplementedError
        yield  # pragma: no cover

    async def embed(self, *a, **k):
        raise NotImplementedError

    async def vision(self, *a, **k):
        raise NotImplementedError


class FakeStreamLLM:
    def __init__(self, parts):
        self._parts = parts

    async def astream(self, messages, *, model=None, params=None):
        for p in self._parts:
            yield TokenChunk(text=p)

    async def generate(self, *a, **k):
        return ""

    async def embed(self, *a, **k):
        return []

    async def vision(self, *a, **k):
        return ""


def _payload_for(llm_route) -> str:
    return json.dumps({"route": llm_route})


async def _final_route(case: dict) -> str:
    node = make_router_node(RouteLLM(_payload_for(case["llm_route"])))
    state = GraphState(messages=[Message(role="user", content=case["user_message"])])
    out = await node(state)
    return route_after_router(GraphState(messages=state.messages, route=out["route"]))


def _load() -> dict:
    return json.loads(_FIXTURE.read_text(encoding="utf-8"))


@pytest.mark.asyncio
async def test_writing_routing_eval_meets_threshold():
    data = _load()
    cases = data["cases"]
    results = [(c["name"], await _final_route(c), c["expected"]) for c in cases]
    failed = [(n, a, e) for n, a, e in results if a != e]
    accuracy = (len(results) - len(failed)) / len(results)
    assert len(cases) >= 5
    assert accuracy >= data["threshold"], f"writing routing accuracy {accuracy:.3f}; failed={failed}"


def test_writing_eval_cases_have_unique_names():
    names = [c["name"] for c in _load()["cases"]]
    assert len(names) == len(set(names))


@pytest.mark.asyncio
async def test_citation_presence_on_grounded_draft():
    node = make_writer_node(LLMWriter(FakeStreamLLM(["Grounded prose [1]."])))
    state = GraphState(
        messages=[Message(role="user", content="Write the chapter on craftsmanship")],
        retrieved_context=[
            RetrievedChunk(chunk_id="c1", score=0.9, content="evidence", document_id="d1", page_from=2)
        ],
    )
    out = await node(state)
    assert out["draft"]
    assert [c.source_id for c in out["citations"]] == ["d1"]  # ⊆ retrieved sources


@pytest.mark.asyncio
async def test_no_citations_without_context():
    node = make_writer_node(LLMWriter(FakeStreamLLM(["Ungrounded."])))
    out = await node(GraphState(messages=[Message(role="user", content="Write the chapter")]))
    assert out["citations"] == []
    assert any(e.message == "empty_context" for e in out["errors"])
