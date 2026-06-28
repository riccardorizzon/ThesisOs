"""M5.2B structural and integration tests for orchestrated graph topology."""

from __future__ import annotations

import pytest

from app.graph.conversation import build_graph
from app.graph.orchestration.constants import DEFAULT_ROUTE, GROUNDED_ROUTE
from app.schemas.graph_state import GraphState, Message
from app.schemas.memory import PromptContext
from app.schemas.retrieval import SearchResultItem
from tests.support.orchestration_llm import OrchestrationLLM

ORCHESTRATION_NODES = frozenset(
    {"supervisor_node", "planner_node", "router_node", "memory_context_node", "retriever_node", "conversation_node"}
)


class SpyRetrieval:
    def __init__(self, results=None):
        self.search_calls = 0
        self._results = results or []

    async def search(self, query, *, filters=None, limit=10, hybrid_alpha=0.5, session=None):
        self.search_calls += 1
        return self._results, "text-multilingual-embedding-002"


@pytest.fixture
def in_memory_checkpointer():
    from langgraph.checkpoint.memory import InMemorySaver

    return InMemorySaver()


def _edge_pairs(graph) -> set[tuple[str, str]]:
    return {(e.source, e.target) for e in graph.edges}


def _conditional_sources(graph) -> set[str]:
    return {e.source for e in graph.edges if e.conditional}


def test_structural_nodes_present(in_memory_checkpointer):
    graph = build_graph(OrchestrationLLM(), checkpointer=in_memory_checkpointer).get_graph()
    node_ids = set(graph.nodes) - {"__start__", "__end__"}
    assert ORCHESTRATION_NODES <= node_ids


def test_structural_orchestration_chain(in_memory_checkpointer):
    edges = _edge_pairs(build_graph(OrchestrationLLM(), checkpointer=in_memory_checkpointer).get_graph())
    assert ("__start__", "supervisor_node") in edges
    assert ("supervisor_node", "planner_node") in edges
    assert ("planner_node", "router_node") in edges
    assert ("router_node", "memory_context_node") in edges


def test_structural_single_conditional_dispatch_point(in_memory_checkpointer):
    graph = build_graph(OrchestrationLLM(), checkpointer=in_memory_checkpointer).get_graph()
    conditional = _conditional_sources(graph)
    assert conditional == {"memory_context_node"}


def test_structural_conditional_edge_targets(in_memory_checkpointer):
    graph = build_graph(OrchestrationLLM(), checkpointer=in_memory_checkpointer).get_graph()
    conditional_edges = [e for e in graph.edges if e.conditional]
    targets = {e.target for e in conditional_edges}
    assert targets == {"conversation_node", "retriever_node"}


def test_structural_grounded_path_through_retriever(in_memory_checkpointer):
    edges = _edge_pairs(build_graph(OrchestrationLLM(), checkpointer=in_memory_checkpointer).get_graph())
    assert ("retriever_node", "conversation_node") in edges
    assert ("conversation_node", "__end__") in edges


def test_structural_no_router_to_retriever_shortcut(in_memory_checkpointer):
    edges = _edge_pairs(build_graph(OrchestrationLLM(), checkpointer=in_memory_checkpointer).get_graph())
    assert ("router_node", "retriever_node") not in edges
    assert ("router_node", "conversation_node") not in edges


def test_structural_no_cycles(in_memory_checkpointer):
    graph = build_graph(OrchestrationLLM(), checkpointer=in_memory_checkpointer).get_graph()
    edges = _edge_pairs(graph)

    def reachable_from(node: str, seen: set[str]) -> None:
        for src, tgt in edges:
            if src == node and tgt not in seen:
                seen.add(tgt)
                reachable_from(tgt, seen)

    seen: set[str] = set()
    reachable_from("__start__", seen)
    assert "supervisor_node" in seen
    assert "__start__" not in seen - {"supervisor_node"}


async def test_integration_conversation_skips_retriever(in_memory_checkpointer):
    spy = SpyRetrieval()
    llm = OrchestrationLLM(route=DEFAULT_ROUTE, stream_parts=["hi"])
    graph = build_graph(
        llm,
        checkpointer=in_memory_checkpointer,
        memory_service=_StubMemory(),
        retrieval_service=spy,
    )
    cfg = {"configurable": {"thread_id": "m5-conv"}}
    async for _ in graph.astream(
        GraphState(messages=[Message(role="user", content="Hello")]),
        cfg,
        stream_mode="custom",
    ):
        pass

    assert spy.search_calls == 0
    assert llm.generate_calls == 3


async def test_integration_grounded_chat_runs_retriever(in_memory_checkpointer):
    results = [
        SearchResultItem(
            chunk_id="c1",
            document_id="d1",
            chunk_hash="h1",
            score=0.9,
            content="Evidence text.",
            document_title="Doc",
        )
    ]
    spy = SpyRetrieval(results)
    llm = OrchestrationLLM(route=GROUNDED_ROUTE, stream_parts=["grounded"])
    graph = build_graph(
        llm,
        checkpointer=in_memory_checkpointer,
        memory_service=_StubMemory(),
        retrieval_service=spy,
    )
    cfg = {"configurable": {"thread_id": "m5-ground"}}
    async for _ in graph.astream(
        GraphState(messages=[Message(role="user", content="Search documents")]),
        cfg,
        stream_mode="custom",
    ):
        pass

    assert spy.search_calls == 1


async def test_integration_route_after_router_drives_branch(in_memory_checkpointer):
    spy = SpyRetrieval()
    graph = build_graph(
        OrchestrationLLM(route=GROUNDED_ROUTE),
        checkpointer=in_memory_checkpointer,
        retrieval_service=spy,
    )
    cfg = {"configurable": {"thread_id": "m5-branch"}}
    final_state = None
    async for _ in graph.astream(
        GraphState(messages=[Message(role="user", content="Find in corpus")]),
        cfg,
        stream_mode="values",
    ):
        final_state = _

    assert final_state is not None
    assert final_state.get("route") == GROUNDED_ROUTE
    assert spy.search_calls == 1


class _StubMemory:
    async def load_prompt_context(self, **kwargs):
        return PromptContext()
