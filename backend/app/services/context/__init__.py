"""Context Engine service (ADR-0038)."""

from app.services.context.exceptions import ProjectNotFoundError
from app.services.context.service import ContextService

__all__ = ["ContextService", "ProjectNotFoundError"]
