"""Grounding regression tests (M4 recovery): retrieved_context must reach the prompt.

Pure graph tests — InMemorySaver + fakes, no Postgres/Vertex. They lock in the
promotion criterion: answers are drawn from retrieved document context, and
retrieved chunk text stays transient (never persisted in message history).
"""

from __future__ import annotations

from app.graph.conversation import build_graph
from app.graph.prompt_wire import render_grounding_prompt
from app.llm.base import TokenChunk
from app.schemas.graph_state import GraphState, Message, RetrievedChunk
from app.schemas.memory import PromptContext
from app.schemas.retrieval import SearchResultItem


class CapturingLLM:
    def __init__(self) -> None:
        self.last_messages: list[dict] | None = None

    async def astream(self, messages, *, model=None, params=None):
        self.last_messages = messages
        yield TokenChunk(text="answer [1]")
        yield TokenChunk(text="", finish_reason="stop", metadata={"usage": {"total_tokens": 2}})

    async def generate(self, *a, **k):
        return "answer"

    async def embed(self, *a, **k):
        raise NotImplementedError

    async def vision(self, *a, **k):
        raise NotImplementedError


class StubMemory:
    async def load_prompt_context(self, *, conversation_id=None, **kwargs):
        return PromptContext()


class FakeRetrieval:
    def __init__(self, results):
        self._results = results

    async def search(self, query, *, filters=None, limit=10, hybrid_alpha=0.5, session=None):
        return self._results, "text-multilingual-embedding-002"


def _graph(llm, results):
    from langgraph.checkpoint.memory import InMemorySaver

    return build_graph(
        llm,
        checkpointer=InMemorySaver(),
        memory_service=StubMemory(),
        retrieval_service=FakeRetrieval(results),
    )


async def _run(graph, msg="What is craftsmanship?"):
    state = GraphState(messages=[Message(role="user", content=msg)])
    cfg = {"configurable": {"thread_id": "g1"}}
    events = []
    async for chunk in graph.astream(state, cfg, stream_mode="custom"):
        events.append(chunk)
    snap = await graph.aget_state(cfg)
    return events, snap


async def test_retrieved_context_injected_into_prompt():
    llm = CapturingLLM()
    chunk_text = "Craftsmanship is the desire to do a job well for its own sake."
    results = [
        SearchResultItem(
            chunk_id="c1",
            document_id="d1",
            chunk_hash="h1",
            score=0.9,
            content=chunk_text,
            document_title="The Craftsman",
            page_from=10,
        )
    ]
    events, _snap = await _run(_graph(llm, results))

    assert llm.last_messages is not None
    system = llm.last_messages[0]
    assert system["role"] == "system"
    assert "Sources:" in system["content"]
    assert "[1]" in system["content"]
    assert chunk_text in system["content"]

    sources = [e for e in events if e.get("type") == "sources"]
    assert sources, "a 'sources' reference event must be emitted"
    first = sources[0]["sources"][0]
    assert first["chunk_id"] == "c1"
    assert first["document_id"] == "d1"


async def test_no_grounding_when_no_results():
    llm = CapturingLLM()
    events, _snap = await _run(_graph(llm, []))
    assert llm.last_messages == [{"role": "user", "content": "What is craftsmanship?"}]
    assert not [e for e in events if e.get("type") == "sources"]


async def test_retrieved_chunks_not_persisted_in_conversation_history():
    llm = CapturingLLM()
    chunk_text = "Craftsmanship is the desire to do a job well for its own sake."
    results = [
        SearchResultItem(
            chunk_id="c1",
            document_id="d1",
            chunk_hash="h1",
            score=0.9,
            content=chunk_text,
            document_title="The Craftsman",
            page_from=10,
        )
    ]
    _events, snap = await _run(_graph(llm, results))

    for msg in snap.values["messages"]:
        assert chunk_text not in msg.content
        assert "Sources:" not in msg.content


def test_render_grounding_prompt_numbers_and_cites():
    chunks = [
        RetrievedChunk(chunk_id="c1", score=0.9, content="Alpha.", document_title="Doc A", page_from=3),
        RetrievedChunk(chunk_id="c2", score=0.7, content="Beta.", document_title="Doc B"),
    ]
    out = render_grounding_prompt(chunks)
    assert "[1] Doc A, p. 3" in out
    assert "[2] Doc B" in out
    assert "Alpha." in out and "Beta." in out


async def test_citations_propagated_to_graph_state():
    llm = CapturingLLM()
    results = [
        SearchResultItem(
            chunk_id="c1",
            document_id="d1",
            chunk_hash="h1",
            score=0.9,
            content="Alpha.",
            document_title="Doc A",
            page_from=3,
        )
    ]
    _events, snap = await _run(_graph(llm, results))

    citations = snap.values["citations"]
    assert len(citations) == 1
    assert citations[0].source_id == "d1"
    assert citations[0].locator == "p.3"
