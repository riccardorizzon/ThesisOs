from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph

from app.graph.inference_enforcement import generate_with_citation_enforcement
from app.graph.academic_production import is_academic_writing_query, last_user_content
from app.graph.memory_context import make_memory_context_node
from app.graph.orchestration.constants import DEFAULT_ROUTE, GROUNDED_ROUTE, WRITER_ROUTE
from app.graph.planner import make_planner_node
from app.graph.prompt_wire import compose_prompt_wire, format_grounding_sources
from app.graph.retriever import make_retriever_node
from app.graph.router import make_router_node
from app.graph.routing import route_after_retriever, route_after_router
from app.graph.supervisor import make_supervisor_node
from app.graph.writer import LLMWriter, make_writer_node
from app.llm.base import LLMClient
from app.runtime.contracts import RuntimeEventEmitter
from app.runtime.events import EventType
from app.runtime.instrumentation import emit_safely, instrument_node, make_event
from app.schemas.graph_state import CitationRef, GraphState, Message, TaskRef
from app.schemas.run_context import RunContext
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
        user_query = last_user_content(state.messages) or ""
        academic = is_academic_writing_query(user_query)

        def _emit(ev: dict) -> None:
            writer(ev)

        text, usage, _retried = await generate_with_citation_enforcement(
            llm,
            wire,
            academic=academic,
            emit=_emit,
        )
        assistant = Message(role="assistant", content=text)
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
    emitter: RuntimeEventEmitter | None = None,
    run_context: RunContext | None = None,
):
    """Orchestrated graph (ADR-0027 + M6 writer route, ADR-0031).

    Topology: supervisor → planner → router → memory_context → [route]:
    conversation → END · grounded_chat → retriever → conversation → END (M5) ·
    writer → retriever → writer → END (M6). M5 paths are byte-for-byte unchanged.

    When an `emitter` + `run_context` are supplied, the Runtime wraps each Business
    node to emit canonical events (M5.4C). Node bodies are untouched (R8/C3)."""
    instrument = emitter is not None and run_context is not None

    def node(name: str, fn, phase: str, *, route_event: bool = False):
        if not instrument:
            return fn
        return instrument_node(
            fn,
            emitter=emitter,
            run_id=run_context.agent_run_id,
            correlation_id=run_context.trace_id,
            agent=name,
            phase=phase,
            route_event=route_event,
        )

    on_task_ref = None
    if task_service is not None:

        async def on_task_ref(task: TaskRef, plan_steps: list[str]) -> None:
            await task_service.upsert_from_task_ref(
                task,
                owner_agent="planner",
                plan_steps=plan_steps,
            )
            if instrument:
                await emit_safely(
                    emitter,
                    make_event(
                        EventType.TASK_PERSISTED,
                        run_id=run_context.agent_run_id,
                        correlation_id=run_context.trace_id,
                        task_id=task.id,
                        title=task.title,
                        status="in_progress",
                    ),
                )

    g = StateGraph(GraphState)
    g.add_node("supervisor_node", node("supervisor", make_supervisor_node(llm), "plan"))
    g.add_node("planner_node", node("planner", make_planner_node(llm, on_task_ref=on_task_ref), "plan"))
    g.add_node("router_node", node("router", make_router_node(llm), "plan", route_event=True))
    g.add_node("memory_context_node", node("memory_context", make_memory_context_node(memory_service), "implement"))
    g.add_node("retriever_node", node("retriever", make_retriever_node(retrieval_service), "implement"))
    g.add_node("conversation_node", node("conversation", make_conversation_node(llm), "implement"))
    # M6 (ADR-0031): writer is a capability behind a port; LLMWriter is the default
    # impl, swappable at this composition root. Streaming is injected via the
    # LangGraph stream writer factory (writer.py imports no LangGraph — C3).
    g.add_node(
        "writer_node",
        node(
            "writer",
            make_writer_node(LLMWriter(llm), stream_writer_factory=get_stream_writer),
            "implement",
        ),
    )

    g.add_edge(START, "supervisor_node")
    g.add_edge("supervisor_node", "planner_node")
    g.add_edge("planner_node", "router_node")
    g.add_edge("router_node", "memory_context_node")
    # Dispatch after memory: conversation skips retrieval; grounded_chat and writer
    # both retrieve first (M5 conversation/grounded paths unchanged — C6).
    g.add_conditional_edges(
        "memory_context_node",
        route_after_router,
        {
            DEFAULT_ROUTE: "conversation_node",
            GROUNDED_ROUTE: "retriever_node",
            WRITER_ROUTE: "retriever_node",
        },
    )
    # After retrieval: grounded_chat → conversation (M5, unchanged); writer → writer.
    g.add_conditional_edges(
        "retriever_node",
        route_after_retriever,
        {
            DEFAULT_ROUTE: "conversation_node",
            WRITER_ROUTE: "writer_node",
        },
    )
    g.add_edge("conversation_node", END)
    g.add_edge("writer_node", END)
    return g.compile(checkpointer=checkpointer)
