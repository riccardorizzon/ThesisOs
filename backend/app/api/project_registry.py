"""Project registry API (PX6-EWO-007)."""

from fastapi import APIRouter

from app.services.project_registry import (
    ProjectCreateRequest,
    ProjectEntry,
    ProjectListResponse,
    ProjectRegistryService,
)

router = APIRouter()
_service = ProjectRegistryService()


@router.get("/projects", response_model=ProjectListResponse)
async def list_projects() -> ProjectListResponse:
    return _service.list_projects()


@router.post("/projects", response_model=ProjectEntry, status_code=201)
async def create_project(body: ProjectCreateRequest) -> ProjectEntry:
    return _service.create_project(body)
