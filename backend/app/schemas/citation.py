"""Citation validation API schemas (PX-6)."""

from __future__ import annotations

from pydantic import BaseModel


class SourceRef(BaseModel):
    source_id: str | None = None
    author: str | None = None
    year: str | int | None = None
    title: str | None = None


class CitationValidateRequest(BaseModel):
    project_id: str | None = None
    text: str
    sources: list[SourceRef] | None = None


class CitationIssueOut(BaseModel):
    start: int
    end: int
    code: str
    message: str
    suggestion: str | None = None
    matched: str = ""


class CitationValidateResponse(BaseModel):
    issues: list[CitationIssueOut]
    blocking: bool
