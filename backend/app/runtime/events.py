"""Runtime Event Contract — canonical Runtime Platform event model (M5.4A).

Public, typed, stable contract for the future Runtime Event Bus (M5.4B). This
module is **Runtime Layer** and intentionally depends on nothing concrete:
no LangGraph, no DB, no LLM, no Business agents (Constitution C3/C4, ADR-0030 §6).

The canonical event vocabulary is centralized in :class:`EventType`. The future
Event Bus emits :class:`RuntimeEvent` instances; subscribers consume them
(`app.runtime.contracts`). No dispatch, persistence, or wiring lives here.

Expected ``metadata`` keys per event type (documented convention — the contract
stays generic so it remains stable and extensible; subscribers read what they need):

| event_type      | typical metadata keys                          |
|-----------------|------------------------------------------------|
| RunStarted      | conversation_id, trace_id                      |
| NodeStarted     | agent, phase ("plan"|"implement"), input (trunc)|
| RouteSelected   | route, errors                                  |
| TaskPersisted   | task_id, title, status                          |
| NodeCompleted   | agent, duration_ms, output (trunc)             |
| NodeFailed      | agent, error, duration_ms                       |
| RunCompleted    | status ("done"|"error"|"cancelled"), task_id   |
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class EventType(str, Enum):
    """Canonical runtime event vocabulary (ADR-0030 §6). Stable per ``m5-complete`` tag;
    adding members is additive, renaming/removing requires an ADR (Constitution C5)."""

    RUN_STARTED = "RunStarted"
    NODE_STARTED = "NodeStarted"
    ROUTE_SELECTED = "RouteSelected"
    TASK_PERSISTED = "TaskPersisted"
    NODE_COMPLETED = "NodeCompleted"
    NODE_FAILED = "NodeFailed"
    RUN_COMPLETED = "RunCompleted"


#: Frozen view of the canonical vocabulary (string values) for stability checks.
EVENT_VOCABULARY: frozenset[str] = frozenset(member.value for member in EventType)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RuntimeEvent(BaseModel):
    """Immutable runtime event value object.

    Carries the minimal stable envelope; event-specific data lives in ``metadata``
    so the contract does not change shape per event type (Constitution C5)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    event_type: EventType
    run_id: str
    timestamp: datetime = Field(default_factory=_utcnow)
    correlation_id: str | None = None
    #: Thesis workspace scope (ADR-0047). Additive, optional — C5 compatible.
    project_id: str | None = None
    metadata: dict = Field(default_factory=dict)
