"""M6.2 writer-route wiring: structural + integration (ADR-0031)."""

from __future__ import annotations

import pytest
from langgraph.checkpoint.memory import InMemorySaver

from app.graph.conversation import build_graph
from app.graph.orchestration.constants import DEFAULT_ROUTE, GROUNDED_ROUTE, WRITER_ROUTE
from app.schemas.graph_state import GraphState, Message
from app.schemas.memory import PromptContext
from app.schemas.retrieval import SearchResultItem
from tests.support.orchestration_llm import OrchestrationLLM


class SpyRetrieval:
    def __init__(self, results=None):
        self.search_calls = 0
        self._results = results or []

    async def search(self, query, *, filters=None, limit=10, hybrid_alpha=0.5, session=None):
        self.search_calls += 1
        return self._results, "text-multilingual-embedding-002"


class _StubMemory:
    async def load_prompt_context(self, **kwargs):
        return PromptContext()


@pytest.fixture
def in_memory_checkpointer():
    from langgraph.checkpoint.memory import InMemorySaver

    return InMemorySaver()


def _edge_pairs(graph) -> set[tuple[str, str]]:
    return {(e.source, e.target) for e in graph.edges}


def _result():
    return SearchResultItem(
        chunk_id="c1",
        document_id="d1",
        chunk_hash="h1",
        score=0.9,
        content="Evidence on craftsmanship.",
        document_title="Doc",
    )


# --- structural -------------------------------------------------------------

def test_structural_writer_node_present(in_memory_checkpointer):
    graph = build_graph(OrchestrationLLM(), checkpointer=in_memory_checkpointer).get_graph()
    assert "writer_node" in (set(graph.nodes) - {"__start__", "__end__"})


def test_structural_writer_path_edges(in_memory_checkpointer):
    edges = _edge_pairs(build_graph(OrchestrationLLM(), checkpointer=in_memory_checkpointer).get_graph())
    # writer is reached only through the retriever, then terminates.
    assert ("retriever_node", "writer_node") in edges
    assert ("writer_node", "__end__") in edges


def test_structural_grounded_path_unchanged(in_memory_checkpointer):
    edges = _edge_pairs(build_graph(OrchestrationLLM(), checkpointer=in_memory_checkpointer).get_graph())
    # M5 grounded path preserved (retriever → conversation → END).
    assert ("retriever_node", "conversation_node") in edges
    assert ("conversation_node", "__end__") in edges


# --- integration ------------------------------------------------------------

async def _run(llm, spy, message, mode="values"):
    graph = build_graph(
        llm,
        checkpointer=InMemorySaver(),
        memory_service=_StubMemory(),
        retrieval_service=spy,
    )
    cfg = {"configurable": {"thread_id": "m6-writer"}}
    final = None
    async for state in graph.astream(
        GraphState(messages=[Message(role="user", content=message)]), cfg, stream_mode=mode
    ):
        final = state
    return final


async def test_writer_route_retrieves_then_drafts():
    spy = SpyRetrieval([_result()])
    llm = OrchestrationLLM(route=WRITER_ROUTE, stream_parts=["Drafted ", "prose."])
    final = await _run(llm, spy, "Write the chapter on craftsmanship")

    assert final is not None
    assert final.get("route") == WRITER_ROUTE
    # Primary query search + Sennett author-doc boost ("craftsmanship" in corpus_query).
    assert spy.search_calls == 2
    assert final.get("draft") == "Drafted prose."
    # citations derived from (⊆) retrieved sources
    assert [c.source_id for c in final.get("citations", [])] == ["d1"]


async def test_writer_route_skips_when_not_drafting():
    # Router emits "writer" but the message is not a drafting request → not writer.
    spy = SpyRetrieval([_result()])
    llm = OrchestrationLLM(route=WRITER_ROUTE, stream_parts=["chatty"])
    final = await _run(llm, spy, "Write me a short poem about the sea")

    assert final.get("route") in {DEFAULT_ROUTE, GROUNDED_ROUTE}
    assert final.get("route") != WRITER_ROUTE


async def test_grounded_route_still_reaches_conversation():
    spy = SpyRetrieval([_result()])
    llm = OrchestrationLLM(route=GROUNDED_ROUTE, stream_parts=["grounded answer"])
    final = await _run(llm, spy, "What do my documents say about craftsmanship")

    assert final.get("route") == GROUNDED_ROUTE
    # Primary query search + Sennett author-doc boost ("craftsmanship" in corpus_query).
    assert spy.search_calls == 2
    assert final.get("draft") == "grounded answer"
