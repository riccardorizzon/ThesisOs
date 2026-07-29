"""Minimal export endpoints (M7 P-EXPORT-MIN)."""

from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, PlainTextResponse

from app.schemas.chapter import ChapterListFilters
from app.services.chapter import ChapterNotFoundError, ChapterService
from app.services.chapter.manuscript_order import render_manuscript_markdown

router = APIRouter(tags=["export"])
_service = ChapterService()


def _err(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"code": code, "message": message})


@router.get("/export/chapters/{chapter_id}.md")
async def export_chapter_markdown(
    chapter_id: str,
    project_id: str = Query(min_length=1),
):
    try:
        chapter = await _service.get(chapter_id)
    except ChapterNotFoundError:
        return _err(404, "chapter_not_found", f"Unknown chapter: {chapter_id}")

    if chapter.project_id != project_id:
        return _err(404, "chapter_not_found", f"Unknown chapter: {chapter_id}")

    content = chapter.content_md or ""
    filename = f"{chapter_id}.md"
    return PlainTextResponse(
        content,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/projects/{project_id}/manuscript.md")
async def export_project_manuscript(project_id: str):
    chapters = await _service.list(
        ChapterListFilters(project_id=project_id, limit=500)
    )
    content = render_manuscript_markdown(chapters)
    return PlainTextResponse(
        content,
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="manuscript.md"',
        },
    )
