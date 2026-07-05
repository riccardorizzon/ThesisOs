"""Projects API — Context Engine endpoint (ADR-0038)."""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from app.schemas.context import (
    DEFAULT_PRODUCT_ID,
    ContextRequest,
    PresentationHint,
    ProjectContext,
)
from app.services.context import ContextService, ProjectNotFoundError

router = APIRouter()
_service = ContextService()


def _err(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"code": code, "message": message})


@router.get("/projects/{project_id}/context")
async def get_project_context(
    project_id: str,
    surface: str = Query(default="writing", description="Presentation hint only"),
    entity_type: str | None = None,
    entity_id: str | None = None,
    selection_anchor: str | None = None,
    product_id: str = Query(default=DEFAULT_PRODUCT_ID),
    workspace_id: str | None = None,
    session_id: str | None = None,
    user_intent: str | None = None,
):
    """Assemble ContextPacket. Surface is a presentation hint — not assembly driver."""
    request = ContextRequest(
        project=ProjectContext(
            project_id=project_id,
            product_id=product_id,
            workspace_id=workspace_id,
            session_id=session_id,
        ),
        presentation=PresentationHint(surface=surface),
        entity_type=entity_type,
        entity_id=entity_id,
        selection_anchor=selection_anchor,
        user_intent=user_intent,
    )
    try:
        return await _service.assemble(request)
    except ProjectNotFoundError as exc:
        return _err(404, "project_not_found", str(exc))
