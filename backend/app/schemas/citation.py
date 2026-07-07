"""Citation validation API schemas (PX-6)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SourceRef(BaseModel):
    author: str | None = None
    year: str | int | None = None
    title: str | None = None


class CitationValidateRequest(BaseModel):
    text: str
    sources: list[SourceRef] = Field(default_factory=list)


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
