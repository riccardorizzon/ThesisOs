"""Knowledge Object API (PX3-EWO-001, PX3-EWO-009 §10)."""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from app.schemas.knowledge_graph import DEFAULT_VISIBLE_NODES, HARD_NODE_LIMIT
from app.services.knowledge import KnowledgeObjectNotFoundError, KnowledgeService
from app.services.knowledge.graph import build_knowledge_graph

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


@router.get("/projects/{project_id}/knowledge/graph")
async def get_knowledge_graph(
    project_id: str,
    focus: str | None = Query(default=None),
    depth: int = Query(default=1, ge=0, le=4),
    max_nodes: int = Query(default=DEFAULT_VISIBLE_NODES, ge=1, le=HARD_NODE_LIMIT),
    view: str | None = Query(default=None),
):
    """Knowledge Graph §10 — bounded concept navigation (read-only)."""
    del project_id
    graph = build_knowledge_graph(
        focus_slug=focus,
        depth=depth,
        max_nodes=max_nodes,
        force_list=view == "list",
    )
    return graph.model_dump(mode="json")
