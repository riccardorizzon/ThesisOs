"""Load read-only workspace snapshot for Companion Loop turns."""

from __future__ import annotations

from app.schemas.chapter import ChapterListFilters, ChapterRecord
from app.schemas.memory import PromptContextFilters
from app.schemas.workspace_snapshot import ChapterSummary, WorkspaceSnapshot
from app.services.chapter import ChapterService
from app.services.memory.service import MemoryService
from app.services.workspace.companion_session import (
    load_last_session_summary,
    parse_focus_from_summary,
    parse_tomorrow_from_summary,
)
from app.services.workspace.work_artifact import load_work_artifact, resume_block
from app.schemas.context import DEFAULT_PROJECT_ID
from app.services.workspace.thesis_knowledge import load_companion_resume, load_project_identity
from app.services.workspace.thesis_sor import reconcile_thesis_agent_memory

_STATUS_FACTOR = {"draft": 0.4, "review": 0.7, "approved": 1.0, "published": 1.0}


def _compute_progress_pct(chapters: list[ChapterRecord]) -> int:
    if not chapters:
        return 0
    weighted = sum(_STATUS_FACTOR.get(ch.status, 0.4) for ch in chapters)
    return round((weighted / len(chapters)) * 100)


def _phase_label(pct: int) -> str:
    if pct == 0:
        return "Prima dei dieci minuti"
    if pct < 40:
        return "Struttura e impostazione"
    if pct < 70:
        return "Sviluppo argomentativo"
    if pct < 100:
        return "Revisione e rifinitura"
    return "Capitoli approvati"


def _to_summary(ch: ChapterRecord) -> ChapterSummary:
    return ChapterSummary(
        id=ch.id,
        title=ch.title,
        status=ch.status,
        word_count=ch.word_count,
        updated_at=ch.updated_at.isoformat() if ch.updated_at else None,
    )


def _pick_focus(chapters: list[ChapterRecord]) -> ChapterRecord | None:
    if not chapters:
        return None
    for status in ("review", "draft"):
        candidates = [ch for ch in chapters if ch.status == status]
        if candidates:
            return max(candidates, key=lambda ch: ch.updated_at)
    return max(chapters, key=lambda ch: ch.updated_at)


class WorkspaceLoader:
    def __init__(
        self,
        *,
        chapter_service: ChapterService | None = None,
        memory_service: MemoryService | None = None,
    ) -> None:
        self._chapters = chapter_service or ChapterService()
        self._memory = memory_service or MemoryService()

    async def load(
        self,
        *,
        project_id: str | None = None,
        conversation_messages: int = 0,
    ) -> WorkspaceSnapshot:
        await reconcile_thesis_agent_memory(self._memory, project_id=project_id)
        chapters = await self._chapters.list(ChapterListFilters())
        progress_pct = _compute_progress_pct(chapters)
        focus = _pick_focus(chapters)

        project_title = "Tesi"
        if project_id in (DEFAULT_PROJECT_ID, None):
            identity = load_project_identity()
            if identity.title:
                project_title = identity.title
        else:
            thesis_ctx = await self._memory.load_prompt_context(
                filters=PromptContextFilters(
                    include_binding_decisions=False,
                    include_editable=False,
                    include_pinned_user=False,
                    include_pinned_thesis=True,
                )
            )
            if thesis_ctx.thesis:
                first = thesis_ctx.thesis[0]
                if first.title:
                    project_title = first.title

        binding_ctx = await self._memory.load_prompt_context(
            filters=PromptContextFilters(
                include_binding_decisions=True,
                include_editable=False,
                include_pinned_user=False,
                include_pinned_thesis=False,
            )
        )

        last_session = await load_last_session_summary(self._memory)
        art = await load_work_artifact(self._memory)
        session_focus = parse_focus_from_summary(last_session)
        if art and art.focus and art.focus.strip():
            session_focus = session_focus or art.focus.strip()
        session_next = parse_tomorrow_from_summary(last_session)
        companion = load_companion_resume(
            last_session_summary=last_session,
            work_artifact=resume_block(art),
            focus_section=session_focus,
            next_action=session_next,
        )

        return WorkspaceSnapshot(
            project_id=project_id,
            project_title=project_title,
            phase=_phase_label(progress_pct),
            progress_pct=progress_pct,
            chapters=[_to_summary(ch) for ch in chapters],
            focus_chapter=_to_summary(focus) if focus else None,
            open_decisions_count=len(binding_ctx.decisions),
            conversation_turns=conversation_messages,
            companion=companion,
        )
