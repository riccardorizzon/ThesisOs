"""Sources module API (PX3-EWO-002)."""

from fastapi import APIRouter, Query

from app.schemas.knowledge import ConfidenceLevel, KnowledgeState
from app.services.sources import SourcesService

router = APIRouter()
_service = SourcesService()


@router.get("/projects/{project_id}/sources")
async def list_sources(
    project_id: str,
    q: str = Query(default=""),
    knowledge_state: KnowledgeState | None = Query(default=None, alias="state"),
    confidence: ConfidenceLevel | None = None,
    include_deprecated: bool = Query(default=False),
):
    del project_id
    return _service.list_sources(
        query=q,
        knowledge_state=knowledge_state,
        confidence=confidence,
        include_deprecated=include_deprecated,
    )
