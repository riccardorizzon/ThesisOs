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
    ChapterNotDeletableError,
    ChapterNotFoundError,
    ChapterService,
    ChapterWriteConflictError,
    InvalidChapterStatusError,
)

router = APIRouter()
_service = ChapterService()


def _err(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"code": code, "message": message})


async def _scope_error(chapter_id: str, project_id: str | None) -> JSONResponse | None:
    """404 when the chapter belongs to another thesis (ADR-0047 INV-MTW-2).

    Scope is enforced only when the caller declares a project; legacy callers
    keep today's behaviour (INV-MTW-1).
    """
    if not project_id:
        return None
    record = await _service.get(chapter_id)
    if record.project_id != project_id:
        return _err(404, "chapter_not_found", f"Chapter not found: {chapter_id}")
    return None


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
    project_id: str = Query(min_length=1),
    parent_id: str | None = None,
    q: str | None = None,
    scope: str = Query(default="all", pattern="^(all|owned|demo)$"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    filters = ChapterListFilters(
        project_id=project_id,
        parent_id=parent_id,
        q=q,
        scope=scope,
        limit=limit,
        offset=offset,
    )
    return await _service.list(filters)


@router.post("/chapters/copy-demo-structure", status_code=201)
async def copy_demo_structure(project_id: str | None = None):
    return await _service.copy_demo_structure(project_id=project_id)


@router.get("/chapters/{chapter_id}")
async def get_chapter(chapter_id: str, project_id: str | None = None):
    try:
        record = await _service.get(chapter_id)
        if project_id and record.project_id != project_id:
            return _err(404, "chapter_not_found", f"Chapter not found: {chapter_id}")
        return record
    except ChapterNotFoundError as exc:
        return _err(404, "chapter_not_found", str(exc))


@router.patch("/chapters/{chapter_id}")
async def update_chapter(chapter_id: str, body: ChapterUpdate, project_id: str | None = None):
    """Update content and/or metadata. A non-null `content_md` → content edit;
    otherwise a metadata/status edit. `expected_version` required (FastAPI 422);
    stale → 409 (ADR-0033)."""
    try:
        scope_err = await _scope_error(chapter_id, project_id)
        if scope_err is not None:
            return scope_err
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
async def list_chapter_versions(chapter_id: str, project_id: str | None = None):
    try:
        scope_err = await _scope_error(chapter_id, project_id)
        if scope_err is not None:
            return scope_err
        return await _service.list_versions(chapter_id)
    except ChapterNotFoundError as exc:
        return _err(404, "chapter_not_found", str(exc))


@router.delete("/chapters/{chapter_id}", status_code=204)
async def delete_chapter(chapter_id: str, project_id: str | None = None):
    try:
        scope_err = await _scope_error(chapter_id, project_id)
        if scope_err is not None:
            return scope_err
        await _service.delete(chapter_id)
    except ChapterNotFoundError as exc:
        return _err(404, "chapter_not_found", str(exc))
    except ChapterNotDeletableError as exc:
        return _err(403, "chapter_not_deletable", str(exc))
