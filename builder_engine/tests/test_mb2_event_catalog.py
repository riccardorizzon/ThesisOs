from __future__ import annotations

from pathlib import Path

import pytest

from builder_engine.events import (
    ALLOWED_EVENT_TYPES,
    DEFAULT_PROGRAM_ID,
    ERA_I_EVENT_TYPES,
    MB2_EXTENSION_EVENT_TYPES,
    BuildEvent,
    BuildEventBus,
    event_now,
)

# MB2 SoR §6.2 — normative Era I baseline.
SOR_ERA_I_EVENTS = frozenset(
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
SOR_MB2_EXTENSION_EVENTS = frozenset(
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


def test_era_catalog_retained():
    assert SOR_ERA_I_EVENTS <= ALLOWED_EVENT_TYPES
    assert ERA_I_EVENT_TYPES == SOR_ERA_I_EVENTS


def test_mb2_catalog_complete():
    assert SOR_MB2_EXTENSION_EVENTS <= ALLOWED_EVENT_TYPES
    assert MB2_EXTENSION_EVENT_TYPES == SOR_MB2_EXTENSION_EVENTS
    assert len(MB2_EXTENSION_EVENT_TYPES) == 14


def test_program_id_required_round_trip():
    ev = event_now("JobReady", {"job_id": "j1"}, program_id="px-exec")
    restored = BuildEvent.from_line(ev.to_line())
    assert restored.program_id == "px-exec"
    assert restored.payload == ev.payload


def test_program_id_defaults_for_legacy_lines():
    line = '{"type":"CycleStarted","timestamp":"t","payload":{}}'
    ev = BuildEvent.from_line(line)
    assert ev.program_id == DEFAULT_PROGRAM_ID


def test_unknown_type_rejected():
    with pytest.raises(ValueError, match="not in catalog"):
        BuildEvent(type="NotInCatalog", timestamp="t", payload={})


def test_append_only_tail_order(tmp_path: Path):
    bus = BuildEventBus(tmp_path)
    bus.publish(event_now("CycleStarted", {"n": 1}))
    bus.publish(event_now("StateObserved", {"n": 2}))
    items = bus.tail(10)
    assert [e.type for e in items] == ["CycleStarted", "StateObserved"]


def test_subscriber_receives_publish(tmp_path: Path):
    bus = BuildEventBus(tmp_path)
    seen: list[str] = []
    bus.subscribe(lambda e: seen.append(e.type))
    bus.publish(event_now("JobReady", {"job_id": "j1"}))
    assert seen == ["JobReady"]


def test_subscriber_idempotent_redelivery(tmp_path: Path):
    bus = BuildEventBus(tmp_path)
    counts: dict[str, int] = {}

    def handler(event: BuildEvent) -> None:
        counts[event.type] = counts.get(event.type, 0) + 1

    bus.subscribe(handler)
    ev = event_now("ProjectionUpdated", {"path": "p.yaml"})
    bus.publish(ev)
    bus.redeliver(ev)
    assert counts["ProjectionUpdated"] == 2


def test_replay_from_offset(tmp_path: Path):
    bus = BuildEventBus(tmp_path)
    bus.publish(event_now("CycleStarted", {"n": 1}))
    bus.publish(event_now("JobClaimed", {"job_id": "j1"}))
    replayed = bus.replay(from_line=1)
    assert len(replayed) == 1
    assert replayed[0].type == "JobClaimed"


def test_all_mb2_extensions_constructable():
    for name in SOR_MB2_EXTENSION_EVENTS:
        ev = event_now(name, {"stub": True})
        assert ev.type == name
