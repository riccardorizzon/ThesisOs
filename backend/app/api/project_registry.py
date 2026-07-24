"""Project registry API (PX6-EWO-007, ADR-0047)."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response

from app.services.project_registry import (
    ProjectConfirmationError,
    ProjectCreateRequest,
    ProjectDeleteRequest,
    ProjectEntry,
    ProjectListResponse,
    ProjectRegistryService,
    ProjectUpdateRequest,
    ProtectedProjectError,
)

router = APIRouter()
_service = ProjectRegistryService()


@router.get("/projects", response_model=ProjectListResponse)
async def list_projects() -> ProjectListResponse:
    return await _service.list_projects()


@router.post("/projects", response_model=ProjectEntry, status_code=201)
async def create_project(body: ProjectCreateRequest) -> ProjectEntry:
    return await _service.create_project(body)


@router.patch("/projects/{project_id}")
async def rename_project(project_id: str, body: ProjectUpdateRequest):
    entry = await _service.rename(project_id, body)
    if entry is None:
        return JSONResponse(
            status_code=404,
            content={"code": "project_not_found", "message": f"Unknown project: {project_id}"},
        )
    return entry


@router.delete("/projects/{project_id}", status_code=204, response_model=None)
async def delete_project(project_id: str, body: ProjectDeleteRequest):
    try:
        deleted = await _service.delete_project(
            project_id,
            confirmation_project_id=body.confirmation_project_id,
        )
    except ProtectedProjectError:
        return JSONResponse(
            status_code=403,
            content={
                "code": "protected_project",
                "message": "Questa tesi è protetta e non può essere eliminata.",
            },
        )
    except ProjectConfirmationError:
        return JSONResponse(
            status_code=422,
            content={
                "code": "project_confirmation_mismatch",
                "message": "La conferma non corrisponde all’ID della tesi.",
            },
        )
    if not deleted:
        return JSONResponse(
            status_code=404,
            content={
                "code": "project_not_found",
                "message": f"Unknown project: {project_id}",
            },
        )
    return Response(status_code=204)
