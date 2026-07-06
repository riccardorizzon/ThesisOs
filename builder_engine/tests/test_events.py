from __future__ import annotations

import json
from pathlib import Path

import pytest

from builder_engine.events import ALLOWED_EVENT_TYPES, BuildEvent, BuildEventBus, event_now


def test_publish_appends_and_tail_returns_order(tmp_path: Path):
    bus = BuildEventBus(tmp_path)
    bus.publish(event_now("CycleStarted", {"n": 1}))
    bus.publish(event_now("StateObserved", {"n": 2}))

    items = bus.tail(10)
    assert len(items) == 2
    assert items[0].type == "CycleStarted"
    assert items[1].type == "StateObserved"


def test_corrupt_line_skipped(tmp_path: Path):
    bus = BuildEventBus(tmp_path)
    bus.path.parent.mkdir(parents=True, exist_ok=True)
    bus.path.write_text('{"type":"CycleStarted","timestamp":"t","payload":{}}\n{bad json\n', encoding="utf-8")
    items = bus.tail(5)
    assert len(items) == 1


def test_unknown_event_type_rejected():
    with pytest.raises(ValueError, match="not in catalog"):
        BuildEvent(type="NotInCatalog", timestamp="t", payload={}, program_id="builder")


def test_catalog_matches_spec_minimum():
    for name in ("StateObserved", "PlanGenerated", "TaskScheduled", "ValidationFailed", "Replanned"):
        assert name in ALLOWED_EVENT_TYPES


def test_round_trip_line():
    ev = event_now("PolicyAllowed", {"ok": True}, cycle_id="abc")
    restored = BuildEvent.from_line(ev.to_line())
    assert restored.type == ev.type
    assert restored.payload == ev.payload
    assert restored.program_id == ev.program_id
