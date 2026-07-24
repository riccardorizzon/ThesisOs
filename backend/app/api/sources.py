"""Sources module API (PX3-EWO-002; PX4-EWO-008)."""

from fastapi import APIRouter, Query
from fastapi.responses import PlainTextResponse, JSONResponse, Response

from app.schemas.knowledge import (
    ConfidenceLevel,
    KnowledgeState,
    SourceListItem,
    SourceListResponse,
)
from app.services.sources.bibliography import export_bibliography_bibtex
from app.services.sources.service import (
    SourceNotDeletableError,
    SourceNotFoundError,
    SourcesService,
)

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
    content = await export_bibliography_bibtex(project_id)
    return PlainTextResponse(
        content,
        media_type="application/x-bibtex",
        headers={
            "Content-Disposition": f'attachment; filename="{project_id}-bibliografia.bib"'
        },
    )


@router.get("/projects/{project_id}/sources", response_model=SourceListResponse)
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


@router.get("/projects/{project_id}/sources/{slug}", response_model=SourceListItem)
async def get_source(project_id: str, slug: str) -> SourceListItem:
    try:
        return await _service.get_source(project_id, slug)
    except SourceNotFoundError:
        return _err(404, "source_not_found", f"Unknown source: {slug}")


@router.post(
    "/projects/{project_id}/sources/{slug}/bibliography",
    response_model=SourceListItem,
)
async def add_source_to_bibliography(
    project_id: str,
    slug: str,
) -> SourceListItem:
    try:
        return await _service.add_to_bibliography(project_id, slug)
    except SourceNotFoundError:
        return _err(404, "source_not_found", f"Unknown source: {slug}")


@router.delete("/projects/{project_id}/sources/{slug}", status_code=204, response_model=None)
async def delete_source(project_id: str, slug: str):
    try:
        await _service.delete_source(project_id, slug)
        return Response(status_code=204)
    except SourceNotFoundError:
        return _err(404, "source_not_found", f"Unknown source: {slug}")
    except SourceNotDeletableError:
        return _err(
            403,
            "source_not_deletable",
            "Solo le fonti caricate dall'utente possono essere eliminate.",
        )
