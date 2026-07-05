"""Knowledge Object API (PX3-EWO-001)."""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from app.services.knowledge import KnowledgeObjectNotFoundError, KnowledgeService

router = APIRouter()
_service = KnowledgeService()


def _err(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"code": code, "message": message})


@router.get("/projects/{project_id}/knowledge/objects")
async def list_knowledge_objects(
    project_id: str,
    type: str | None = Query(default=None, alias="type"),
    include_deprecated: bool = Query(default=False),
):
    """List Knowledge Object envelopes for a project (read-only catalog)."""
    del project_id  # single-project v0; project scoping in later EWO
    return _service.list_objects(object_type=type, include_deprecated=include_deprecated)


@router.get("/projects/{project_id}/knowledge/objects/{slug}")
async def get_knowledge_object(project_id: str, slug: str):
    del project_id
    try:
        return _service.get_object(slug)
    except KnowledgeObjectNotFoundError:
        return _err(404, "knowledge_object_not_found", f"Unknown knowledge object: {slug}")


@router.get("/projects/{project_id}/knowledge/concepts/{slug}")
async def get_concept_detail(project_id: str, slug: str):
    """Explain Page concept detail (PX3-EWO-005)."""
    del project_id
    try:
        return _service.get_concept_detail(slug)
    except KnowledgeObjectNotFoundError:
        return _err(404, "concept_not_found", f"Unknown concept: {slug}")


@router.get("/projects/{project_id}/knowledge/concepts/{slug}/header")
async def get_concept_header(project_id: str, slug: str):
    """Explain Page region A (PX3-EWO-006)."""
    del project_id
    try:
        return _service.get_concept_header(slug)
    except KnowledgeObjectNotFoundError:
        return _err(404, "concept_not_found", f"Unknown concept: {slug}")


@router.get("/projects/{project_id}/knowledge/concepts/{slug}/definition")
async def get_concept_definition(project_id: str, slug: str):
    """Explain Page region B (PX3-EWO-006)."""
    del project_id
    try:
        return _service.get_concept_definition(slug)
    except KnowledgeObjectNotFoundError:
        return _err(404, "concept_not_found", f"Unknown concept: {slug}")
