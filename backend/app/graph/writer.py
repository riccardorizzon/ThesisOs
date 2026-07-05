"""Writer capability + graph node (M6, ADR-0031).

The writer is a **capability/port** — `write_grounded(brief) -> DraftResult` —
not hard-coded logic. Today it is implemented by `LLMWriter`; tomorrow a
`writer-v2`/`writer-fast`/… can be swapped at the composition root with no
topology change (C8; ADR-0030 R1/R2).

Purity (ADR-0031 §3, Constitution C3): this module imports no `app.db`,
`app.runtime`, `app.services.chapter`, telemetry, or LangGraph. Streaming is
delivered through an injected `emit` callback (transport-agnostic), and the
LangGraph stream writer is supplied by the Runtime at wiring time (M6.2) via
`stream_writer_factory` — never imported here.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from app.graph.inference_enforcement import generate_with_citation_enforcement
from app.graph.orchestration.writer_prompt import (
    allowed_citation_source_ids,
    build_citations,
    compose_writer_wire,
    compose_writing_panel_wire,
    filter_citations,
)
from app.graph.prompt_wire import format_grounding_sources
from app.llm.base import LLMClient
from app.schemas.draft import DraftResult, WriterBrief
from app.schemas.graph_state import AgentError, GraphState, Message, RetrievedChunk

Emit = Callable[[dict], None]


class WriterGenerationError(Exception):
    """A WriterCapability could not generate a draft (→ `generation_failed`)."""


class WriterCapability(Protocol):
    """Stable writer port. `emit`, when provided, streams chunks to the caller."""

    async def write_grounded(
        self, brief: WriterBrief, *, emit: Emit | None = None
    ) -> DraftResult: ...


class LLMWriter:
    """Default `WriterCapability`: streams grounded prose from the injected LLM seam."""

    def __init__(self, llm: LLMClient):
        self._llm = llm

    async def write_grounded(
        self, brief: WriterBrief, *, emit: Emit | None = None
    ) -> DraftResult:
        wire = [{"role": m.role, "content": m.content} for m in compose_writer_wire(brief)]

        def _emit(ev: dict) -> None:
            if emit is not None:
                emit(ev)

        try:
            draft, usage, _retried = await generate_with_citation_enforcement(
                self._llm,
                wire,
                academic=True,
                emit=_emit if emit is not None else None,
            )
        except Exception as exc:  # noqa: BLE001 — surfaced as generation_failed by the node
            raise WriterGenerationError(str(exc)) from exc
        citations = build_citations(brief.retrieved_context)
        metrics: dict = {
            "draft_chars": len(draft),
            "source_count": len(brief.retrieved_context),
        }
        if usage:
            metrics["usage"] = usage
        return DraftResult(
            draft=draft,
            citations=citations,
            metadata={"writer": "llm"},
            metrics=metrics,
        )

    async def run_panel_action(
        self,
        *,
        action: str,
        selection_text: str | None,
        chapter_content: str,
        context_summary: str | None,
        retrieved_context: list[RetrievedChunk],
        emit: Emit | None = None,
    ) -> DraftResult:
        """Lateral writing-panel action with context packet (PX2-EWO-003)."""
        wire = [
            {"role": m.role, "content": m.content}
            for m in compose_writing_panel_wire(
                action=action,
                selection_text=selection_text,
                chapter_content=chapter_content,
                context_summary=context_summary,
                retrieved_context=retrieved_context,
            )
        ]

        def _emit(ev: dict) -> None:
            if emit is not None:
                emit(ev)

        try:
            draft, usage, _retried = await generate_with_citation_enforcement(
                self._llm,
                wire,
                academic=True,
                emit=_emit if emit is not None else None,
            )
        except Exception as exc:  # noqa: BLE001
            raise WriterGenerationError(str(exc)) from exc

        citations = build_citations(retrieved_context)
        metrics: dict = {
            "draft_chars": len(draft),
            "source_count": len(retrieved_context),
        }
        if usage:
            metrics["usage"] = usage
        return DraftResult(
            draft=draft,
            citations=citations,
            metadata={"writer": "llm", "writing_panel_action": action},
            metrics=metrics,
        )


async def run_writing_panel_action(
    writer: LLMWriter,
    *,
    action: str,
    selection_text: str | None,
    chapter_content: str,
    context_summary: str | None,
    retrieved_context: list[RetrievedChunk],
    emit: Emit | None = None,
) -> DraftResult:
    """Writing-panel entry — delegates to `LLMWriter.run_panel_action`."""
    return await writer.run_panel_action(
        action=action,
        selection_text=selection_text,
        chapter_content=chapter_content,
        context_summary=context_summary,
        retrieved_context=retrieved_context,
        emit=emit,
    )


def make_writer_node(
    writer: WriterCapability,
    *,
    stream_writer_factory: Callable[[], Emit] | None = None,
):
    """Adapt a `WriterCapability` into a graph-callable node (ADR-0031 §2/§3).

    Maps `DraftResult` → `{messages(+assistant), draft, citations, errors}` only —
    exactly `contracts/agents/writer.json`. `metadata`/`reasoning`/`metrics` ride the
    stream, never GraphState. `stream_writer_factory` (Runtime-injected at wiring)
    yields the transport `emit`; absent it, the node is silent (M6.1 / tests).
    """

    async def writer_node(state: GraphState) -> dict:
        errors = list(state.errors)
        brief = WriterBrief(
            plan=state.plan,
            retrieved_context=list(state.retrieved_context),
            messages=list(state.messages),
        )

        if not brief.retrieved_context:
            errors.append(AgentError(agent="writer", message="empty_context"))

        emit = stream_writer_factory() if stream_writer_factory is not None else None
        if emit is not None and state.retrieved_context:
            emit(
                {
                    "type": "sources",
                    "text": "",
                    "sources": format_grounding_sources(state.retrieved_context),
                }
            )

        try:
            result = await writer.write_grounded(brief, emit=emit)
        except WriterGenerationError:
            errors.append(AgentError(agent="writer", message="generation_failed"))
            return {"errors": errors}

        citations = filter_citations(
            result.citations, allowed_citation_source_ids(state.retrieved_context)
        )
        if emit is not None and result.metrics.get("usage"):
            emit({"type": "usage", "text": "", "usage": result.metrics["usage"]})

        assistant = Message(role="assistant", content=result.draft)
        return {
            "messages": [*state.messages, assistant],
            "draft": result.draft,
            "citations": citations,
            "errors": errors,
        }

    return writer_node
