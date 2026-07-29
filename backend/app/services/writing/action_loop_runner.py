"""Writing panel action loop orchestrator (ADR-0049 Phase 3)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from app.graph.inference_enforcement import generate_with_citation_enforcement
from app.graph.orchestration.writer_prompt import (
    WRITING_PANEL_ACTIONS,
    build_citations,
    compose_writing_panel_wire,
)
from app.graph.writer import WriterGenerationError
from app.llm.base import LLMClient
from app.runtime.action_loop.loop import ActionLoopRunner
from app.runtime.action_loop.permissions import PermissionEngine
from app.runtime.action_loop.tools import build_panel_tools
from app.runtime.action_loop.types import ActionLoopContext, AssistantTurn, LoopStep
from app.schemas.draft import DraftResult
from app.schemas.graph_state import RetrievedChunk
from app.services.retrieval import EmbedFailedError, RetrievalService
from app.services.writing.panel import WritingPanelRetrievalError

_MAX_LOOP_ITERATIONS = 6
_MAX_CHAPTER_EXCERPT = 4000


def _build_retrieval_messages(ctx: ActionLoopContext) -> list[dict[str, Any]]:
    action_instruction = WRITING_PANEL_ACTIONS.get(
        ctx.action,
        "Assist the operator with the requested writing action.",
    )
    system_parts = [
        "You are a research assistant for the ThesisOS writing panel.",
        f"Action: {ctx.action}",
        f"Task:\n{action_instruction}",
        (
            "Use the search_corpus tool to find evidence in the thesis corpus. "
            "Run multiple searches with different queries until you have enough "
            "material to support the final response. "
            "You may also use get_selection_context to review the passage and chapter."
        ),
    ]
    if ctx.context_summary and ctx.context_summary.strip():
        system_parts.append(f"Context packet summary:\n{ctx.context_summary.strip()}")
    if ctx.selection_text and ctx.selection_text.strip():
        system_parts.append(f"Selected passage:\n{ctx.selection_text.strip()}")
    chapter = ctx.chapter_content.strip()
    if chapter:
        system_parts.append(f"Chapter content (reference):\n{chapter[:_MAX_CHAPTER_EXCERPT]}")

    user_content = (
        f"Search the corpus for evidence relevant to the '{ctx.action}' action. "
        "Call search_corpus as needed, then stop when you have sufficient sources."
    )
    return [
        {"role": "system", "content": "\n\n".join(system_parts)},
        {"role": "user", "content": user_content},
    ]


async def run_writing_panel_with_loop(
    *,
    llm: LLMClient,
    action: str,
    project_id: str | None,
    selection_text: str | None,
    chapter_content: str,
    context_summary: str | None,
    on_step: Callable[[LoopStep], None] | None = None,
    emit: Callable[[dict], None] | None = None,
    complete: Callable[
        [list[dict[str, Any]], list[dict[str, Any]]], Awaitable[AssistantTurn]
    ]
    | None = None,
    retrieval_service: RetrievalService | None = None,
) -> DraftResult:
    """Two-phase pipeline: retrieval tool loop, then grounded draft generation."""
    ctx = ActionLoopContext(
        action=action,
        project_id=project_id,
        selection_text=selection_text,
        chapter_content=chapter_content,
        context_summary=context_summary,
    )
    accumulated: list[RetrievedChunk] = []
    service = retrieval_service or RetrievalService()

    async def default_complete(
        messages: list[dict[str, Any]], tools: list[dict[str, Any]]
    ) -> AssistantTurn:
        return await llm.acompletion_with_tools(messages, tools=tools)

    complete_fn = complete or default_complete

    registry = build_panel_tools(ctx, service, accumulated)
    runner = ActionLoopRunner(
        registry=registry,
        permissions=PermissionEngine(workspace_root=Path("/tmp")),
        complete=complete_fn,
        max_iterations=_MAX_LOOP_ITERATIONS,
    )

    try:
        loop_result = await runner.run(_build_retrieval_messages(ctx), on_step=on_step)
    except EmbedFailedError as exc:
        raise WritingPanelRetrievalError(str(exc)) from exc

    search_count = sum(1 for tc in loop_result.tool_calls if tc.name == "search_corpus")

    wire = [
        {"role": m.role, "content": m.content}
        for m in compose_writing_panel_wire(
            action=action,
            selection_text=selection_text,
            chapter_content=chapter_content,
            context_summary=context_summary,
            retrieved_context=accumulated,
        )
    ]

    def _emit(ev: dict) -> None:
        if emit is not None:
            emit(ev)

    try:
        draft, usage, _retried = await generate_with_citation_enforcement(
            llm,
            wire,
            academic=True,
            emit=_emit if emit is not None else None,
        )
    except Exception as exc:  # noqa: BLE001 — surfaced as generation_failed by API
        raise WriterGenerationError(str(exc)) from exc

    citations = build_citations(accumulated)
    metrics: dict = {
        "draft_chars": len(draft),
        "source_count": len(accumulated),
        "search_count": search_count,
        "chunk_count": len(accumulated),
    }
    if usage:
        metrics["usage"] = usage

    return DraftResult(
        draft=draft,
        citations=citations,
        metadata={
            "writer": "llm",
            "writing_panel_action": action,
            "loop_action": True,
            "search_count": search_count,
            "chunk_count": len(accumulated),
        },
        metrics=metrics,
    )
