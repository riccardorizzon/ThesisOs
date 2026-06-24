from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

VALID_KINDS = frozenset({"user", "thesis", "concept", "citation", "decision", "editable"})
SINGLETON_KINDS = frozenset({"user", "thesis", "editable"})
CANONICAL_KEYS: dict[str, str] = {"user": "user", "thesis": "thesis", "editable": "editable"}
PROMPT_CONTEXT_KINDS = frozenset({"editable", "user", "thesis"})


class MemoryRecord(BaseModel):
    id: str
    kind: str
    title: str | None
    content: str
    metadata: dict = Field(default_factory=dict)
    key: str | None = None
    pinned: bool = False
    source: str = "user"
    version: int
    created_at: datetime
    updated_at: datetime


class MemoryCreate(BaseModel):
    kind: str
    content: str
    title: str | None = None
    metadata: dict = Field(default_factory=dict)
    key: str | None = None
    pinned: bool = False
    source: str = "user"


class MemoryUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    metadata: dict | None = None
    pinned: bool | None = None
    expected_version: int


class MemoryListFilters(BaseModel):
    kind: str | None = None
    key: str | None = None
    pinned: bool | None = None
    q: str | None = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class MemoryVersionRecord(BaseModel):
    memory_id: str
    version: int
    title: str | None
    content: str
    metadata: dict = Field(default_factory=dict)
    source: str
    changed_at: datetime


class PromptContextFilters(BaseModel):
    include_editable: bool = True
    include_pinned_user: bool = True
    include_pinned_thesis: bool = True


class PromptMemoryItem(BaseModel):
    id: str
    kind: str
    title: str | None
    content: str
    version: int
    pinned: bool
    key: str | None = None


class PromptContext(BaseModel):
    """Stable output contract for load_prompt_context — not a rendered string."""

    editable: list[PromptMemoryItem] = Field(default_factory=list)
    user: list[PromptMemoryItem] = Field(default_factory=list)
    thesis: list[PromptMemoryItem] = Field(default_factory=list)
    conversation_id: str | None = None
