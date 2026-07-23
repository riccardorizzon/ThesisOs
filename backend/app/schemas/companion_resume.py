"""Structured companion resume — Sprint 1 CONTINUE (Thesis Companion v1)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CompanionResume(BaseModel):
    focus_chapter: str = "Capitolo 3"
    focus_section: str = "§3.6"
    focus_section_title: str = ""
    focus_status: str = "in stesura"
    backlog: list[str] = Field(default_factory=list)
    next_action: str = ""
    session_notes: list[str] = Field(default_factory=list)
    key_decisions: list[str] = Field(default_factory=list)
    section_text: str | None = None
    last_session_summary: str | None = None
    work_artifact: str | None = None
