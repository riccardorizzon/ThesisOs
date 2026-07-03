"""Project scope resolution stub — PX1-EWO-006."""

from __future__ import annotations

from app.schemas.context import DEFAULT_PROJECT_ID, ProjectContext
from app.services.context.exceptions import ProjectNotFoundError

KNOWN_PROJECTS = frozenset({DEFAULT_PROJECT_ID})


def resolve_project_context(project: ProjectContext) -> ProjectContext:
    """PX-1 stub: validate known projects. Multi-tenant resolution deferred to PX-2+."""
    if project.project_id not in KNOWN_PROJECTS:
        raise ProjectNotFoundError(project.project_id)
    return project
