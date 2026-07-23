"""Document domain DTOs (M3). Maps to tables `documents`, `document_versions`,
`chunks`. No embedding/vector fields in M3 (spec §2, §5)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

# Accepted import formats. PDF/EPUB/DOCX (M3) + native markdown/text (M4 recovery, P4).
VALID_SOURCE_TYPES = frozenset({"pdf", "epub", "docx", "markdown", "text"})

# Closed status set (spec §2.1). `indexed` is RESERVED for M4 — never set in M3.
M3_STATUSES = frozenset({"uploaded", "processing", "parsed", "failed"})
TERMINAL_SUCCESS_STATUS = "parsed"

_EXTENSION_SOURCE_TYPE = {
    ".pdf": "pdf",
    ".epub": "epub",
    ".docx": "docx",
    ".md": "markdown",
    ".markdown": "markdown",
    ".txt": "text",
}


def infer_source_type(filename: str | None) -> str | None:
    """Map a filename extension to a source_type, or None if unknown."""
    if not filename or "." not in filename:
        return None
    ext = filename[filename.rfind(".") :].lower()
    return _EXTENSION_SOURCE_TYPE.get(ext)


class DocumentChunk(BaseModel):
    """Domain chunk — maps to table `chunks`. No embedding fields in M3 (spec §5)."""

    id: str
    document_id: str
    chunk_index: int
    chunk_hash: str
    content: str
    page_from: int | None = None
    page_to: int | None = None
    section_path: str | None = None
    token_count: int | None = None
    metadata: dict = Field(default_factory=dict)
    created_at: datetime


class DocumentRecord(BaseModel):
    id: str
    project_id: str = "thesis-agent"
    title: str
    author: str | None = None
    source_type: str
    original_filename: str | None = None
    gcs_uri: str | None = None
    status: str
    page_count: int | None = None
    language: str | None = None
    version: int
    parser: str | None = None
    parsed_at: datetime | None = None
    chunk_count: int | None = None
    error_message: str | None = None
    metadata: dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class DocumentUploadMetadata(BaseModel):
    title: str | None = None
    author: str | None = None
    language: str | None = None
    project_id: str | None = None  # ADR-0047: None ⇒ Default Thesis
    metadata: dict = Field(default_factory=dict)


class DocumentUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    language: str | None = None
    metadata: dict | None = None
    expected_version: int


class DocumentListFilters(BaseModel):
    project_id: str | None = None  # ADR-0047: None ⇒ Default Thesis
    source_type: str | None = None
    status: str | None = None
    q: str | None = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class DocumentVersionRecord(BaseModel):
    document_id: str
    version: int
    title: str
    author: str | None = None
    source_type: str
    page_count: int | None = None
    chunk_count: int | None = None
    parser: str | None = None
    metadata: dict = Field(default_factory=dict)
    change_reason: str
    changed_at: datetime
