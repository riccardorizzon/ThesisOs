"""API envelope for companion resume + project identity."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.companion_resume import CompanionResume


class CompanionResumePacket(BaseModel):
    schema_version: str = "1"
    project_id: str
    title: str = ""
    author: str = ""
    institution: str = ""
    migration_run: str | None = None
    progress_summary: str = ""
    continue_prompt: str = "Continuiamo da ieri"
    focus_chapter_id: str | None = None
    resume: CompanionResume = Field(default_factory=CompanionResume)
