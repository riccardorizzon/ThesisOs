"""Thin HTTP adapter for chapters (M6) — validation + ChapterService delegation +
error mapping only. No DB session here; ChapterService is the sole writer (ADR-0032).
"""

from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from app.schemas.chapter import (
    ChapterContentUpdate,
    ChapterCreate,
    ChapterListFilters,
    ChapterMetadataUpdate,
    ChapterReorderRequest,
    ChapterUpdate,
)
from app.services.chapter import (
    ChapterNotFoundError,
    ChapterService,
    ChapterWriteConflictError,
    InvalidChapterStatusError,
)

router = APIRouter()
_service = ChapterService()


def _err(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"code": code, "message": message})


@router.patch("/chapters/reorder")
async def reorder_chapters(body: ChapterReorderRequest):
    try:
        return await _service.reorder(body)
    except ChapterNotFoundError as exc:
        return _err(404, "chapter_not_found", str(exc))


@router.post("/chapters", status_code=201)
async def create_chapter(body: ChapterCreate):
    try:
        return await _service.create(body)
    except InvalidChapterStatusError as exc:
        return _err(422, "invalid_status", str(exc))


@router.get("/chapters")
async def list_chapters(
    parent_id: str | None = None,
    q: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    filters = ChapterListFilters(parent_id=parent_id, q=q, limit=limit, offset=offset)
    return await _service.list(filters)


@router.get("/chapters/{chapter_id}")
async def get_chapter(chapter_id: str):
    try:
        return await _service.get(chapter_id)
    except ChapterNotFoundError as exc:
        return _err(404, "chapter_not_found", str(exc))


@router.patch("/chapters/{chapter_id}")
async def update_chapter(chapter_id: str, body: ChapterUpdate):
    """Update content and/or metadata. A non-null `content_md` → content edit;
    otherwise a metadata/status edit. `expected_version` required (FastAPI 422);
    stale → 409 (ADR-0033)."""
    try:
        if body.content_md is not None:
            return await _service.update_content(
                chapter_id,
                ChapterContentUpdate(
                    content_md=body.content_md, expected_version=body.expected_version
                ),
            )
        return await _service.update_metadata(
            chapter_id,
            ChapterMetadataUpdate(
                title=body.title,
                summary=body.summary,
                status=body.status,
                expected_version=body.expected_version,
            ),
        )
    except ChapterNotFoundError as exc:
        return _err(404, "chapter_not_found", str(exc))
    except ChapterWriteConflictError as exc:
        return _err(409, "write_conflict", str(exc))
    except InvalidChapterStatusError as exc:
        return _err(422, "invalid_status", str(exc))


@router.get("/chapters/{chapter_id}/versions")
async def list_chapter_versions(chapter_id: str):
    try:
        return await _service.list_versions(chapter_id)
    except ChapterNotFoundError as exc:
        return _err(404, "chapter_not_found", str(exc))
