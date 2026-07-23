from langchain_core.runnables import RunnableConfig
from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph

from app.graph.academic_production import is_academic_writing_query, last_user_content
from app.graph.companion.enforcement import (
    CompanionEnforceContext,
    generate_with_companion_enforcement,
)
from app.graph.companion.prompts import (
    OPENING_09_00_HINT,
    PRESERVE_HINT,
    SAVE_HINT,
)
from app.graph.companion.review_state import (
    REVIEW_PHASE_HINTS,
    choice_label,
    choice_made,
)
from app.graph.inference_enforcement import (
    MINIMAL_REASONING_PARAMS,
    generate_with_citation_enforcement,
)
from app.graph.memory_context import make_memory_context_node
from app.graph.orchestration.constants import DEFAULT_ROUTE, GROUNDED_ROUTE, WRITER_ROUTE
from app.graph.planner import make_planner_node
from app.graph.prompt_wire import compose_prompt_wire, format_grounding_sources
from app.graph.retriever import make_retriever_node
from app.graph.router import make_router_node
from app.graph.routing import route_after_retriever, route_after_router
from app.graph.supervisor import make_supervisor_node
from app.graph.workspace_context import make_workspace_context_node
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
from app.services.workspace.persistence import (
    PersistenceTier,
    classify_persistence,
    focus_from_resume,
    next_action_from_resume,
    persist_turn,
    persistence_failure_text,
)
from app.services.workspace.snapshot import WorkspaceLoader
from app.services.workspace.thesis_sor import THESIS_AGENT_PROJECT_ID


def _companion_enforce_context(state: GraphState) -> CompanionEnforceContext:
    system_messages = {
        message.content for message in state.messages if message.role == "system"
    }
    review_phase = next(
        (
            phase
            for phase, hint in REVIEW_PHASE_HINTS.items()
            if hint in system_messages
        ),
        None,
    )
    utterance = last_user_content(state.messages)
    return CompanionEnforceContext(
        opening=OPENING_09_00_HINT in system_messages,
        preserve=PRESERVE_HINT in system_messages,
        save=SAVE_HINT in system_messages,
        review_phase=review_phase,
        choice_made=choice_made(utterance),
    )


def _prior_assistant_content(messages: list[Message]) -> str | None:
    for message in reversed(messages):
        if message.role == "assistant" and (message.content or "").strip():
            return message.content
    return None


def make_conversation_node(
    llm: LLMClient,
    *,
    memory_service: MemoryService | None = None,
):
    async def conversation_node(state: GraphState, config: RunnableConfig) -> dict:
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
        errors = list(state.errors)

        def _emit(ev: dict) -> None:
            writer(ev)

        project_id = (config.get("configurable") or {}).get("project_id")
        if project_id == THESIS_AGENT_PROJECT_ID:
            companion_ctx = _companion_enforce_context(state)
            # Resume is the single source of truth for focus + next action
            # (parsed back from the same [COMPANION RESUME] block the model sees).
            system_contents = [
                m.content for m in state.messages if m.role == "system"
            ]
            focus = focus_from_resume(system_contents)

            async def generate_cited(candidate_wire: list[dict]) -> tuple[str, dict]:
                cited_text, cited_usage, _ = (
                    await generate_with_citation_enforcement(
                        llm,
                        candidate_wire,
                        academic=academic,
                    )
                )
                return cited_text, cited_usage

            generate = generate_cited if academic else None
            text, usage, _retried = (
                await generate_with_companion_enforcement(
                    llm,
                    wire,
                    ctx=companion_ctx,
                    emit=_emit,
                    focus=focus,
                    choice_label=choice_label(user_query),
                    generate=generate,
                    params=None if academic else MINIMAL_REASONING_PARAMS,
                )
            )

            # Persistence contract (ADR-0046): PRESERVE/SAVE turns must write
            # before the confirmation stands. NO WRITE = NO SAVE.
            tier = classify_persistence(
                preserve=companion_ctx.preserve,
                save=companion_ctx.save,
            )
            if tier is not PersistenceTier.NONE:
                outcome = await persist_turn(
                    memory_service or MemoryService(),
                    tier=tier,
                    user_text=user_query,
                    assistant_text=text,
                    prior_assistant=_prior_assistant_content(state.messages),
                    focus=focus,
                    next_action=next_action_from_resume(system_contents),
                )
                if not outcome.persisted:
                    text = persistence_failure_text(tier, focus=focus)
                    writer({"type": "replace", "text": text})
                    errors.append(f"persistence_failed:{tier.value}")
        else:
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
            "errors": errors,
        }

    return conversation_node


def build_graph(
    llm: LLMClient,
    *,
    orchestration_llm: LLMClient | None = None,
    checkpointer,
    memory_service: MemoryService | None = None,
    workspace_loader: WorkspaceLoader | None = None,
    retrieval_service: RetrievalService | None = None,
    task_service: TaskService | None = None,
    emitter: RuntimeEventEmitter | None = None,
    run_context: RunContext | None = None,
):
    """Orchestrated graph (ADR-0027 + M6 writer route, ADR-0031).

    Topology: supervisor → planner → router → workspace_context → memory_context → [route]:
    conversation → END · grounded_chat → retriever → conversation → END (M5) ·
    writer → retriever → writer → END (M6). M5 paths are byte-for-byte unchanged.

    When an `emitter` + `run_context` are supplied, the Runtime wraps each Business
    node to emit canonical events (M5.4C). Node bodies are untouched (R8/C3)."""
    instrument = emitter is not None and run_context is not None
    orchestrator = llm if orchestration_llm is None else orchestration_llm

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
    g.add_node(
        "supervisor_node",
        node("supervisor", make_supervisor_node(orchestrator), "plan"),
    )
    g.add_node(
        "planner_node",
        node(
            "planner",
            make_planner_node(orchestrator, on_task_ref=on_task_ref),
            "plan",
        ),
    )
    g.add_node(
        "router_node",
        node("router", make_router_node(orchestrator), "plan", route_event=True),
    )
    g.add_node(
        "workspace_context_node",
        node(
            "workspace_context",
            make_workspace_context_node(workspace_loader, memory_service=memory_service),
            "implement",
        ),
    )
    g.add_node("memory_context_node", node("memory_context", make_memory_context_node(memory_service), "implement"))
    g.add_node("retriever_node", node("retriever", make_retriever_node(retrieval_service), "implement"))
    g.add_node(
        "conversation_node",
        node(
            "conversation",
            make_conversation_node(llm, memory_service=memory_service),
            "implement",
        ),
    )
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
    g.add_edge("router_node", "workspace_context_node")
    g.add_edge("workspace_context_node", "memory_context_node")
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
