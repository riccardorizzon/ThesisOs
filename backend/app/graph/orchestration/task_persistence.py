"""Planner task persistence hook — composition root wires TaskService (M5.3)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from app.schemas.graph_state import TaskRef

# Planner produces TaskRef; runtime composition root maps it to TaskService.
PlannerTaskPersistHook = Callable[[TaskRef, list[str]], Awaitable[None]]
