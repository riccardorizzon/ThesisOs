"""Sources module API (PX3-EWO-002; PX4-EWO-008)."""

from fastapi import APIRouter, Query
from fastapi.responses import PlainTextResponse, JSONResponse

from app.schemas.knowledge import ConfidenceLevel, KnowledgeState
from app.services.sources.bibliography import export_bibliography_bibtex
from app.services.sources.service import SourceNotFoundError, SourcesService

router = APIRouter()
_service = SourcesService()


def _err(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"code": code, "message": message})


@router.get("/projects/{project_id}/sources/bibliography/export")
async def export_bibliography(
    project_id: str,
    format: str = Query(default="bibtex", pattern="^(bibtex)$"),
):
    if format != "bibtex":
        return _err(422, "unsupported_format", f"Unsupported format: {format}")
    content = export_bibliography_bibtex(project_id)
    return PlainTextResponse(
        content,
        media_type="application/x-bibtex",
        headers={
            "Content-Disposition": f'attachment; filename="{project_id}-bibliografia.bib"'
        },
    )


@router.get("/projects/{project_id}/sources")
async def list_sources(
    project_id: str,
    q: str = Query(default=""),
    knowledge_state: KnowledgeState | None = Query(default=None, alias="state"),
    confidence: ConfidenceLevel | None = None,
    include_deprecated: bool = Query(default=False),
):
    return await _service.list_sources(
        project_id,
        query=q,
        knowledge_state=knowledge_state,
        confidence=confidence,
        include_deprecated=include_deprecated,
    )


@router.get("/projects/{project_id}/sources/{slug}")
async def get_source(project_id: str, slug: str):
    try:
        return await _service.get_source(project_id, slug)
    except SourceNotFoundError:
        return _err(404, "source_not_found", f"Unknown source: {slug}")
