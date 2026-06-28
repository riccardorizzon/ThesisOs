from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph

from app.graph.memory_context import make_memory_context_node
from app.graph.orchestration.constants import DEFAULT_ROUTE, GROUNDED_ROUTE
from app.graph.planner import make_planner_node
from app.graph.prompt_wire import compose_prompt_wire, format_grounding_sources
from app.graph.retriever import make_retriever_node
from app.graph.router import make_router_node
from app.graph.routing import route_after_router
from app.graph.supervisor import make_supervisor_node
from app.llm.base import LLMClient
from app.schemas.graph_state import CitationRef, GraphState, Message, TaskRef
from app.services.memory.service import MemoryService
from app.services.retrieval.service import RetrievalService
from app.services.task.service import TaskService


def make_conversation_node(llm: LLMClient):
    async def conversation_node(state: GraphState) -> dict:
        writer = get_stream_writer()
        wire_messages = compose_prompt_wire(state)
        if state.retrieved_context:
            writer(
                {
                    "type": "sources",
                    "text": "",
                    "sources": format_grounding_sources(state.retrieved_context),
                }
            )
        wire = [{"role": m.role, "content": m.content} for m in wire_messages]
        parts: list[str] = []
        usage: dict = {}
        async for chunk in llm.astream(wire):
            if chunk.text:
                parts.append(chunk.text)
                writer({"type": "token", "text": chunk.text})
            if chunk.metadata.get("usage"):
                usage = chunk.metadata["usage"]
        assistant = Message(role="assistant", content="".join(parts))
        # Task 9 reads usage from the custom stream (not from GraphState),
        # which keeps GraphState frozen (ADR-0007) and avoids a Pydantic
        # unknown-key update error. "text" is included so every custom
        # chunk is shape-compatible with token chunks for stream consumers.
        if usage:
            writer({"type": "usage", "text": "", "usage": usage})
        citations = [
            CitationRef(
                source_id=c.document_id or c.chunk_id,
                locator=(f"p.{c.page_from}" if c.page_from else c.chunk_id),
            )
            for c in state.retrieved_context
        ]
        # Replace semantics: the caller owns message history (DB is the
        # system of record), so no add_messages reducer is needed.
        return {
            "messages": [*state.messages, assistant],
            "draft": assistant.content,
            "citations": citations,
            "errors": list(state.errors),
        }

    return conversation_node


def build_graph(
    llm: LLMClient,
    *,
    checkpointer,
    memory_service: MemoryService | None = None,
    retrieval_service: RetrievalService | None = None,
    task_service: TaskService | None = None,
):
    """M5 graph (ADR-0027): orchestration chain + conditional execution subgraph."""
    on_task_ref = None
    if task_service is not None:

        async def on_task_ref(task: TaskRef, plan_steps: list[str]) -> None:
            await task_service.upsert_from_task_ref(
                task,
                owner_agent="planner",
                plan_steps=plan_steps,
            )

    g = StateGraph(GraphState)
    g.add_node("supervisor_node", make_supervisor_node(llm))
    g.add_node("planner_node", make_planner_node(llm, on_task_ref=on_task_ref))
    g.add_node("router_node", make_router_node(llm))
    g.add_node("memory_context_node", make_memory_context_node(memory_service))
    g.add_node("retriever_node", make_retriever_node(retrieval_service))
    g.add_node("conversation_node", make_conversation_node(llm))

    g.add_edge(START, "supervisor_node")
    g.add_edge("supervisor_node", "planner_node")
    g.add_edge("planner_node", "router_node")
    g.add_edge("router_node", "memory_context_node")
    g.add_conditional_edges(
        "memory_context_node",
        route_after_router,
        {
            DEFAULT_ROUTE: "conversation_node",
            GROUNDED_ROUTE: "retriever_node",
        },
    )
    g.add_edge("retriever_node", "conversation_node")
    g.add_edge("conversation_node", END)
    return g.compile(checkpointer=checkpointer)
