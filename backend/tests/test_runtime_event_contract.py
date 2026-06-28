"""Runtime Event Contract tests (M5.4A) — model validity, vocabulary stability,
serialization, contract conformance, and absence of concrete dependencies."""

from __future__ import annotations

import inspect
import os
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

import app
from app.runtime import contracts as contracts_module
from app.runtime import events as events_module
from app.runtime import (
    EVENT_VOCABULARY,
    EventType,
    RuntimeEvent,
    RuntimeEventEmitter,
    RuntimeSubscriber,
)

EXPECTED_VOCABULARY = frozenset(
    {
        "RunStarted",
        "NodeStarted",
        "RouteSelected",
        "TaskPersisted",
        "NodeCompleted",
        "NodeFailed",
        "RunCompleted",
    }
)

FORBIDDEN_IMPORT_MARKERS = (
    "langgraph",
    "sqlalchemy",
    "app.db",
    "app.graph",
    "app.services",
    "app.llm",
)


# --- Event model validity --------------------------------------------------

def test_runtime_event_required_fields_and_defaults():
    event = RuntimeEvent(event_type=EventType.RUN_STARTED, run_id="run-1")

    assert event.event_type is EventType.RUN_STARTED
    assert event.run_id == "run-1"
    assert event.correlation_id is None
    assert event.metadata == {}
    assert event.timestamp.tzinfo is not None  # timezone-aware


def test_runtime_event_accepts_metadata_and_correlation():
    event = RuntimeEvent(
        event_type=EventType.NODE_COMPLETED,
        run_id="run-2",
        correlation_id="trace-9",
        metadata={"agent": "planner", "duration_ms": 12},
    )
    assert event.correlation_id == "trace-9"
    assert event.metadata["agent"] == "planner"


def test_runtime_event_rejects_unknown_event_type():
    with pytest.raises(ValidationError):
        RuntimeEvent(event_type="NotARealEvent", run_id="run-3")


def test_runtime_event_forbids_extra_fields():
    with pytest.raises(ValidationError):
        RuntimeEvent(event_type=EventType.RUN_STARTED, run_id="run-4", agent="planner")


def test_runtime_event_is_immutable():
    event = RuntimeEvent(event_type=EventType.RUN_STARTED, run_id="run-5")
    with pytest.raises(ValidationError):
        event.run_id = "mutated"


# --- Vocabulary stability --------------------------------------------------

def test_event_vocabulary_is_centralized_and_stable():
    assert {member.value for member in EventType} == EXPECTED_VOCABULARY
    assert EVENT_VOCABULARY == EXPECTED_VOCABULARY
    assert len(EventType) == 7


def test_event_type_values_match_canonical_names():
    assert EventType.RUN_STARTED.value == "RunStarted"
    assert EventType.NODE_FAILED.value == "NodeFailed"
    assert EventType.RUN_COMPLETED.value == "RunCompleted"


# --- Serialization ---------------------------------------------------------

def test_runtime_event_json_roundtrip():
    original = RuntimeEvent(
        event_type=EventType.ROUTE_SELECTED,
        run_id="run-6",
        correlation_id="corr-1",
        metadata={"route": "grounded_chat", "errors": []},
        timestamp=datetime(2026, 6, 28, 16, 0, tzinfo=timezone.utc),
    )
    restored = RuntimeEvent.model_validate_json(original.model_dump_json())
    assert restored == original


def test_runtime_event_serializes_event_type_as_string():
    event = RuntimeEvent(event_type=EventType.TASK_PERSISTED, run_id="run-7")
    assert '"TaskPersisted"' in event.model_dump_json()


# --- Contract conformance --------------------------------------------------

def test_subscriber_protocol_conformance():
    class GoodSubscriber:
        async def on_event(self, event: RuntimeEvent) -> None:
            return None

    class BadSubscriber:
        async def handle(self, event: RuntimeEvent) -> None:
            return None

    assert isinstance(GoodSubscriber(), RuntimeSubscriber)
    assert not isinstance(BadSubscriber(), RuntimeSubscriber)


def test_emitter_protocol_conformance():
    class GoodEmitter:
        async def emit(self, event: RuntimeEvent) -> None:
            return None

    class BadEmitter:
        async def publish(self, event: RuntimeEvent) -> None:
            return None

    assert isinstance(GoodEmitter(), RuntimeEventEmitter)
    assert not isinstance(BadEmitter(), RuntimeEventEmitter)


# --- Independence from concrete layers -------------------------------------

@pytest.mark.parametrize("module", [events_module, contracts_module])
def test_contract_modules_have_no_concrete_dependencies(module):
    source = inspect.getsource(module)
    for marker in FORBIDDEN_IMPORT_MARKERS:
        assert marker not in source, f"{module.__name__} must not depend on {marker}"


def test_no_app_code_depends_on_runtime_contract_yet():
    """Acceptance: the contract exists but nothing wires to it yet (M5.4A)."""
    app_root = os.path.dirname(app.__file__)
    runtime_dir = os.path.join(app_root, "runtime")
    offenders: list[str] = []
    for dirpath, _dirs, files in os.walk(app_root):
        if dirpath.startswith(runtime_dir):
            continue
        for name in files:
            if not name.endswith(".py"):
                continue
            path = os.path.join(dirpath, name)
            with open(path, encoding="utf-8") as fh:
                if "app.runtime" in fh.read():
                    offenders.append(os.path.relpath(path, app_root))
    assert offenders == [], f"unexpected dependents on app.runtime: {offenders}"
