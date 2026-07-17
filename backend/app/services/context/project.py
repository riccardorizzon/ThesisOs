"""Project scope resolution — registry-backed (CUR-7 hard isolation)."""

from __future__ import annotations

from app.schemas.context import ProjectContext
from app.services.context.exceptions import ProjectNotFoundError
from app.services.project_registry import ProjectRegistryService

_registry = ProjectRegistryService()


def resolve_project_context(project: ProjectContext) -> ProjectContext:
    """Validate project_id against the live project registry."""
    if not _registry.has(project.project_id):
        raise ProjectNotFoundError(project.project_id)
    return project
