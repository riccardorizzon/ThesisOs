"""Workspace snapshot for Companion Loop v0 — read-only turn context."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.companion_resume import CompanionResume


class ChapterSummary(BaseModel):
    id: str
    title: str
    status: str
    word_count: int = 0
    updated_at: str | None = None


class WorkspaceSnapshot(BaseModel):
    project_id: str | None = None
    project_title: str = "Tesi"
    phase: str = "Prima dei dieci minuti"
    progress_pct: int = Field(default=0, ge=0, le=100)
    chapters: list[ChapterSummary] = Field(default_factory=list)
    focus_chapter: ChapterSummary | None = None
    open_decisions_count: int = 0
    conversation_turns: int = 0
    companion: CompanionResume | None = None
