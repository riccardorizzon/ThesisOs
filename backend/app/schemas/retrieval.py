"""Retrieval API and service DTOs (M4)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.graph_state import RetrievedChunk


class SearchFilters(BaseModel):
    document_ids: list[str] | None = None
    source_types: list[str] | None = None


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=10, ge=1, le=100)
    document_ids: list[str] | None = None
    source_types: list[str] | None = None
    hybrid_alpha: float = Field(default=0.5, ge=0.0, le=1.0)


class SearchResultItem(BaseModel):
    chunk_id: str
    document_id: str
    chunk_hash: str
    score: float
    content: str
    document_title: str
    page_from: int | None = None
    page_to: int | None = None


class SearchResponse(BaseModel):
    results: list[SearchResultItem]
    query_embedding_model: str


__all__ = [
    "RetrievedChunk",
    "SearchFilters",
    "SearchRequest",
    "SearchResponse",
    "SearchResultItem",
]
