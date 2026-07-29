"""POST /writing/actions — lateral Writing panel AI actions (PX2-EWO-003)."""

from __future__ import annotations

import json

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from app.graph.writer import LLMWriter, WriterGenerationError, run_writing_panel_action
from app.llm.base import NotConfiguredLLM
from app.llm.factory import get_llm_client
from app.runtime.action_loop.types import LoopStep
from app.services.writing.action_loop_runner import run_writing_panel_with_loop
from app.services.writing.panel import (
    WritingPanelRetrievalError,
    fetch_panel_retrieved_context,
)

router = APIRouter(prefix="/writing", tags=["writing"])

VALID_ACTIONS = frozenset({"rewrite", "verify", "find-sources", "expand"})
LOOP_ACTIONS = frozenset({"verify", "find-sources"})


class WritingActionRequest(BaseModel):
    action: str = Field(min_length=1, max_length=64)
    project_id: str | None = None  # ADR-0047: None ⇒ Default Thesis
    chapter_id: str | None = None
    selection_text: str | None = None
    chapter_content: str = ""
    context_summary: str | None = None


@router.post("/actions")
async def writing_actions(req: WritingActionRequest):
    if req.action not in VALID_ACTIONS:
        return JSONResponse(
            status_code=400,
            content={"code": "invalid_action", "message": f"Unknown action: {req.action}"},
        )

    llm = get_llm_client()
    if isinstance(llm, NotConfiguredLLM):
        return JSONResponse(
            status_code=503,
            content={"code": "llm_not_configured", "message": "LLM runtime not configured"},
        )

    retrieved_context = None
    if req.action not in LOOP_ACTIONS:
        try:
            retrieved_context = await fetch_panel_retrieved_context(
                action=req.action,
                selection_text=req.selection_text,
                chapter_content=req.chapter_content,
                project_id=req.project_id,
            )
        except WritingPanelRetrievalError as exc:
            return JSONResponse(
                status_code=422,
                content={"code": "embed_failed", "message": str(exc)},
            )

    writer = LLMWriter(llm)

    async def event_gen():
        tokens: list[str] = []
        loop_steps: list[LoopStep] = []

        def emit(ev: dict) -> None:
            text = ev.get("text")
            if text:
                tokens.append(text)

        def on_step(step: LoopStep) -> None:
            loop_steps.append(step)

        try:
            if req.action in LOOP_ACTIONS:
                result = await run_writing_panel_with_loop(
                    llm=llm,
                    action=req.action,
                    project_id=req.project_id,
                    selection_text=req.selection_text,
                    chapter_content=req.chapter_content,
                    context_summary=req.context_summary,
                    on_step=on_step,
                    emit=emit,
                )
            else:
                result = await run_writing_panel_action(
                    writer,
                    action=req.action,
                    selection_text=req.selection_text,
                    chapter_content=req.chapter_content,
                    context_summary=req.context_summary,
                    retrieved_context=retrieved_context or [],
                    emit=emit,
                )
        except WritingPanelRetrievalError as exc:
            yield {
                "event": "error",
                "data": json.dumps({"code": "embed_failed", "message": str(exc)}),
            }
            return
        except WriterGenerationError as exc:
            yield {
                "event": "error",
                "data": json.dumps({"code": "generation_failed", "message": str(exc)}),
            }
            return

        for step in loop_steps:
            yield {
                "event": "step",
                "data": json.dumps(
                    {
                        "phase": "retrieval",
                        "label": step.label,
                        "detail": step.detail,
                    }
                ),
            }

        draft = result.draft
        if not tokens and draft:
            chunk_size = max(1, len(draft) // 8)
            for i in range(0, len(draft), chunk_size):
                piece = draft[i : i + chunk_size]
                yield {"event": "token", "data": json.dumps({"text": piece})}
        else:
            for piece in tokens:
                yield {"event": "token", "data": json.dumps({"text": piece})}

        done_payload: dict = {"draft": draft}
        if req.action in LOOP_ACTIONS and result.metadata:
            meta: dict = {}
            if "search_count" in result.metadata:
                meta["search_count"] = result.metadata["search_count"]
            if "chunk_count" in result.metadata:
                meta["chunk_count"] = result.metadata["chunk_count"]
            if meta:
                done_payload["meta"] = meta

        yield {"event": "done", "data": json.dumps(done_payload)}

    return EventSourceResponse(event_gen(), ping=15)
