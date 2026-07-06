"""Knowledge Object API (PX3-EWO-001 read; PX4-EWO-003 CRUD)."""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, Response

from app.schemas.knowledge import ConceptCreate, ConceptUpdate
from app.schemas.knowledge_graph import DEFAULT_VISIBLE_NODES, HARD_NODE_LIMIT
from app.services.knowledge import (
    ConceptNotFoundError,
    ConceptSlugExistsError,
    KnowledgeObjectNotFoundError,
    KnowledgeService,
)
from app.services.knowledge.graph import build_knowledge_graph_for_project
from app.services.knowledge_search import search_concepts

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
    """List Knowledge Object envelopes for a project."""
    return await _service.list_objects_async(
        project_id=project_id,
        object_type=type,
        include_deprecated=include_deprecated,
    )


@router.get("/projects/{project_id}/knowledge/objects/{slug}")
async def get_knowledge_object(project_id: str, slug: str):
    try:
        return await _service.get_object_async(project_id, slug)
    except KnowledgeObjectNotFoundError:
        return _err(404, "knowledge_object_not_found", f"Unknown knowledge object: {slug}")


@router.post("/projects/{project_id}/knowledge/concepts", status_code=201)
async def create_concept(project_id: str, body: ConceptCreate):
    try:
        return await _service.create_concept(project_id, body)
    except ConceptSlugExistsError as exc:
        return _err(409, "concept_slug_exists", str(exc))


@router.patch("/projects/{project_id}/knowledge/concepts/{slug}")
async def update_concept(project_id: str, slug: str, body: ConceptUpdate):
    try:
        return await _service.update_concept(project_id, slug, body)
    except ConceptNotFoundError:
        return _err(404, "concept_not_found", f"Unknown concept: {slug}")


@router.delete("/projects/{project_id}/knowledge/concepts/{slug}", status_code=204, response_model=None)
async def delete_concept(project_id: str, slug: str):
    try:
        await _service.delete_concept(project_id, slug)
        return Response(status_code=204)
    except ConceptNotFoundError:
        return _err(404, "concept_not_found", f"Unknown concept: {slug}")


@router.get("/projects/{project_id}/knowledge/concepts/{slug}")
async def get_concept_detail(project_id: str, slug: str):
    """Explain Page concept detail (PX3-EWO-005)."""
    try:
        return await _service.get_concept_detail_async(project_id, slug)
    except KnowledgeObjectNotFoundError:
        return _err(404, "concept_not_found", f"Unknown concept: {slug}")


@router.get("/projects/{project_id}/knowledge/concepts/{slug}/header")
async def get_concept_header(project_id: str, slug: str):
    """Explain Page region A (PX3-EWO-006)."""
    try:
        return await _service.get_concept_header_async(project_id, slug)
    except KnowledgeObjectNotFoundError:
        return _err(404, "concept_not_found", f"Unknown concept: {slug}")


@router.get("/projects/{project_id}/knowledge/concepts/{slug}/definition")
async def get_concept_definition(project_id: str, slug: str):
    """Explain Page region B (PX3-EWO-006)."""
    try:
        return await _service.get_concept_definition_async(project_id, slug)
    except KnowledgeObjectNotFoundError:
        return _err(404, "concept_not_found", f"Unknown concept: {slug}")


@router.get("/projects/{project_id}/knowledge/search")
async def search_knowledge(
    project_id: str,
    q: str = Query(min_length=1),
    limit: int = Query(default=20, ge=1, le=100),
):
    """Ranked concept search across Knowledge objects (PX4-EWO-007)."""
    results = await search_concepts(project_id, q, limit=limit)
    return {"query": q, "results": results, "total": len(results)}


@router.get("/projects/{project_id}/knowledge/graph")
async def get_knowledge_graph(
    project_id: str,
    focus: str | None = Query(default=None),
    depth: int = Query(default=1, ge=0, le=4),
    max_nodes: int = Query(default=DEFAULT_VISIBLE_NODES, ge=1, le=HARD_NODE_LIMIT),
    view: str | None = Query(default=None),
):
    """Knowledge Graph §10 — bounded concept navigation (read-only)."""
    graph = await build_knowledge_graph_for_project(
        project_id,
        focus_slug=focus,
        depth=depth,
        max_nodes=max_nodes,
        force_list=view == "list",
    )
    return graph.model_dump(mode="json")
