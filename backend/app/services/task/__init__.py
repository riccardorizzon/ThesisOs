"""TaskService — sole write port for the tasks domain (M5, ADR-0027)."""

from app.services.task.service import TaskService

__all__ = ["TaskService"]
