"""Project registry API (PX6-EWO-007, ADR-0047)."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.services.project_registry import (
    ProjectCreateRequest,
    ProjectEntry,
    ProjectListResponse,
    ProjectRegistryService,
    ProjectUpdateRequest,
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
