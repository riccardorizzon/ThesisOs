"""Build event bus — append-only sidecar log (MB2 D4)."""

from __future__ import annotations

import json
import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# MB2 SoR §6.2 — Era I baseline (retained).
ERA_I_EVENT_TYPES = frozenset(
    {
        "SnapshotCreated",
        "StateObserved",
        "PolicyAllowed",
        "PolicyBlocked",
        "PlanGenerated",
        "PlanEmpty",
        "TaskScheduled",
        "LockAcquired",
        "ValidationPassed",
        "ValidationFailed",
        "StateUpdated",
        "WaveAdvanced",
        "MergeAccepted",
        "MergeRejected",
        "Replanned",
        "RecoveryTaskCreated",
        "WorkerDispatched",
        "WorkerReported",
        "CycleStarted",
        "CycleHalted",
        "EventsPublished",
    }
)

# MB2 SoR §6.3 — normative extensions.
MB2_EXTENSION_EVENT_TYPES = frozenset(
    {
        "ExecutionGraphDerived",
        "JobReady",
        "JobClaimed",
        "EwoCompleted",
        "MergeCompleted",
        "MergeFailed",
        "IntegrationStarted",
        "IntegrationPassed",
        "IntegrationFailed",
        "QwoSpawned",
        "QwoPassed",
        "QwoFailed",
        "RuntimeEscalated",
        "ProjectionUpdated",
    }
)

ALLOWED_EVENT_TYPES = ERA_I_EVENT_TYPES | MB2_EXTENSION_EVENT_TYPES

DEFAULT_PROGRAM_ID = "builder"


@dataclass(frozen=True)
class BuildEvent:
    type: str
    timestamp: str
    payload: dict[str, Any]
    program_id: str = DEFAULT_PROGRAM_ID
    cycle_id: str | None = None

    def __post_init__(self) -> None:
        if self.type not in ALLOWED_EVENT_TYPES:
            raise ValueError(f"event type not in catalog: {self.type}")
        if not self.program_id:
            raise ValueError("program_id is required")

    def to_line(self) -> str:
        return json.dumps(
            {
                "type": self.type,
                "timestamp": self.timestamp,
                "program_id": self.program_id,
                "payload": self.payload,
                "cycle_id": self.cycle_id,
            },
            separators=(",", ":"),
        )

    @classmethod
    def from_line(cls, line: str) -> BuildEvent:
        data = json.loads(line)
        event_type = str(data["type"])
        if event_type not in ALLOWED_EVENT_TYPES:
            raise ValueError(f"unknown event type: {event_type}")
        return cls(
            type=event_type,
            timestamp=str(data.get("timestamp") or ""),
            payload=dict(data.get("payload") or {}),
            program_id=str(data.get("program_id") or DEFAULT_PROGRAM_ID),
            cycle_id=data.get("cycle_id"),
        )


EventHandler = Callable[[BuildEvent], None]


@dataclass
class BuildEventBus:
    repo_root: Path
    path: Path = field(init=False)
    _handlers: list[EventHandler] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        self.repo_root = self.repo_root.resolve()
        self.path = self.repo_root / ".builder-engine" / "events.jsonl"

    def subscribe(self, handler: EventHandler) -> None:
        self._handlers.append(handler)

    def publish(self, event: BuildEvent) -> None:
        if event.type not in ALLOWED_EVENT_TYPES:
            raise ValueError(f"event type not in catalog: {event.type}")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(event.to_line() + "\n")
        self._dispatch(event)

    def publish_many(self, events: list[BuildEvent]) -> None:
        for event in events:
            self.publish(event)

    def redeliver(self, event: BuildEvent) -> None:
        """Re-dispatch an already-persisted event (at-least-once within process)."""
        self._dispatch(event)

    def _dispatch(self, event: BuildEvent) -> None:
        for handler in self._handlers:
            try:
                handler(event)
            except Exception:
                logger.exception("event handler failed for %s", event.type)

    def replay(self, *, from_line: int = 0) -> list[BuildEvent]:
        if not self.path.is_file():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()
        result: list[BuildEvent] = []
        for line in lines[from_line:]:
            if not line.strip():
                continue
            try:
                result.append(BuildEvent.from_line(line))
            except (json.JSONDecodeError, ValueError, KeyError):
                continue
        return result

    def tail(self, n: int = 20) -> list[BuildEvent]:
        if not self.path.is_file() or n <= 0:
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()
        result: list[BuildEvent] = []
        for line in lines[-n:]:
            if not line.strip():
                continue
            try:
                result.append(BuildEvent.from_line(line))
            except (json.JSONDecodeError, ValueError, KeyError):
                continue
        return result


def new_cycle_id() -> str:
    return uuid.uuid4().hex[:12]


def event_now(
    event_type: str,
    payload: dict[str, Any],
    *,
    program_id: str = DEFAULT_PROGRAM_ID,
    cycle_id: str | None = None,
) -> BuildEvent:
    return BuildEvent(
        type=event_type,
        timestamp=datetime.now(UTC).isoformat(),
        payload=payload,
        program_id=program_id,
        cycle_id=cycle_id,
    )
