"""Thin HTTP adapter for hybrid corpus search (M4)."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.retrieval import SearchFilters, SearchRequest, SearchResponse
from app.services.retrieval import EmbedFailedError, RetrievalService

router = APIRouter()
_service = RetrievalService()


def _err(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"code": code, "message": message})


@router.post("/search")
async def search_corpus(body: SearchRequest):
    if not body.query.strip():
        return _err(400, "empty_query", "query must not be empty")
    try:
        results, model = await _service.search(
            body.query.strip(),
            filters=SearchFilters(
                project_id=body.project_id,
                document_ids=body.document_ids,
                source_types=body.source_types,
            ),
            limit=body.limit,
            hybrid_alpha=body.hybrid_alpha,
        )
    except EmbedFailedError as exc:
        return _err(422, "embed_failed", str(exc))
    return SearchResponse(results=results, query_embedding_model=model)
