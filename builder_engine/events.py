"""Build event bus — append-only sidecar log (MB2 D4)."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# MB2 spec §3 D4 / L2 §7 catalog — no ad-hoc event names.
ALLOWED_EVENT_TYPES = frozenset(
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


@dataclass(frozen=True)
class BuildEvent:
    type: str
    timestamp: str
    payload: dict[str, Any]
    cycle_id: str | None = None

    def __post_init__(self) -> None:
        if self.type not in ALLOWED_EVENT_TYPES:
            raise ValueError(f"event type not in catalog: {self.type}")

    def to_line(self) -> str:
        return json.dumps(
            {
                "type": self.type,
                "timestamp": self.timestamp,
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
            cycle_id=data.get("cycle_id"),
        )


@dataclass
class BuildEventBus:
    repo_root: Path
    path: Path = field(init=False)

    def __post_init__(self) -> None:
        self.repo_root = self.repo_root.resolve()
        self.path = self.repo_root / ".builder-engine" / "events.jsonl"

    def publish(self, event: BuildEvent) -> None:
        if event.type not in ALLOWED_EVENT_TYPES:
            raise ValueError(f"event type not in catalog: {event.type}")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(event.to_line() + "\n")

    def publish_many(self, events: list[BuildEvent]) -> None:
        for event in events:
            self.publish(event)

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


def event_now(event_type: str, payload: dict[str, Any], *, cycle_id: str | None = None) -> BuildEvent:
    return BuildEvent(
        type=event_type,
        timestamp=datetime.now(UTC).isoformat(),
        payload=payload,
        cycle_id=cycle_id,
    )
