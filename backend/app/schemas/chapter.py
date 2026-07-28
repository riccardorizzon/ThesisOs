"""Chapter domain DTOs (M6). Maps to tables `chapters`, `chapter_versions`.

No retrieval/embedding fields — chapters are authored prose, not a RAG surface
(ADR-0032 §6).
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from app.schemas.context import DEFAULT_PROJECT_ID

# Chapter lifecycle (ADR-0032 §3). M6 wires draft/review; approved (M9 Critic) and
# published (M8) are reserved values the API accepts but does not auto-transition.
VALID_CHAPTER_STATUSES = frozenset({"draft", "review", "approved", "published"})

# Change-stream kinds (ADR-0033 §2). M6 emits WRITE/EDIT/PROMOTE; MERGE/RESTORE reserved.
CHANGE_KINDS = frozenset({"WRITE", "EDIT", "PROMOTE", "MERGE", "RESTORE"})

ChapterTitle = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=200),
]


class ChapterRecord(BaseModel):
    id: str
    project_id: str = DEFAULT_PROJECT_ID
    parent_id: str | None = None
    order_index: int
    title: str
    status: str
    content_md: str | None = None
    summary: str | None = None
    word_count: int
    version: int
    created_at: datetime
    updated_at: datetime
    deletable: bool = False


class ChapterVersionRecord(BaseModel):
    chapter_id: str
    version: int
    change_kind: str
    title: str
    status: str
    content_md: str | None = None
    summary: str | None = None
    word_count: int
    metadata: dict = Field(default_factory=dict)
    changed_at: datetime


class ChapterCreate(BaseModel):
    title: ChapterTitle
    project_id: str = DEFAULT_PROJECT_ID
    parent_id: str | None = None
    order_index: int = 0
    status: str = "draft"
    content_md: str | None = None
    summary: str | None = None


class ChapterContentUpdate(BaseModel):
    content_md: str
    expected_version: int


class ChapterMetadataUpdate(BaseModel):
    title: ChapterTitle | None = None
    summary: str | None = None
    status: str | None = None
    expected_version: int


class ChapterUpdate(BaseModel):
    """Unified PATCH body (matches OpenAPI `ChapterUpdate`).

    `content_md` present (non-null) → content edit; otherwise a metadata/status edit.
    """

    content_md: str | None = None
    title: ChapterTitle | None = None
    summary: str | None = None
    status: str | None = None
    expected_version: int


class ChapterListFilters(BaseModel):
    # HTTP GET /chapters requires project_id; internal callers may still omit.
    project_id: str | None = None
    parent_id: str | None = None
    q: str | None = None
    scope: str = "all"
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


class CopyDemoStructureResponse(BaseModel):
    created: list[ChapterRecord] = Field(default_factory=list)
    skipped_titles: list[str] = Field(default_factory=list)


class ChapterReorderRequest(BaseModel):
    project_id: str = Field(min_length=1)
    ordered_ids: list[str] = Field(min_length=1)
