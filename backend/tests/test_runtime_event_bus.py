"""Runtime Event Bus tests (M5.4B) — fan-out, ordering, non-blocking, purity."""

from __future__ import annotations

import inspect

import pytest

from app.runtime import RuntimeEvent, RuntimeEventBus, RuntimeEventEmitter
from app.runtime import event_bus as event_bus_module
from app.runtime.events import EventType

FORBIDDEN_IMPORT_MARKERS = (
    "langgraph",
    "sqlalchemy",
    "app.db",
    "app.graph",
    "app.services",
    "app.llm",
)


class RecordingSubscriber:
    def __init__(self) -> None:
        self.received: list[RuntimeEvent] = []

    async def on_event(self, event: RuntimeEvent) -> None:
        self.received.append(event)


class FailingSubscriber:
    def __init__(self) -> None:
        self.calls = 0

    async def on_event(self, event: RuntimeEvent) -> None:
        self.calls += 1
        raise RuntimeError("subscriber boom")


def _event(event_type: EventType = EventType.RUN_STARTED, run_id: str = "run-1") -> RuntimeEvent:
    return RuntimeEvent(event_type=event_type, run_id=run_id)


def test_bus_conforms_to_emitter_protocol():
    assert isinstance(RuntimeEventBus(), RuntimeEventEmitter)


@pytest.mark.asyncio
async def test_emit_fans_out_to_all_subscribers():
    a, b = RecordingSubscriber(), RecordingSubscriber()
    bus = RuntimeEventBus([a, b])
    event = _event()

    await bus.emit(event)

    assert a.received == [event]
    assert b.received == [event]


@pytest.mark.asyncio
async def test_zero_subscribers_emit_is_silent_noop():
    bus = RuntimeEventBus()
    await bus.emit(_event())  # must not raise


@pytest.mark.asyncio
async def test_subscribe_registers_dynamically():
    bus = RuntimeEventBus()
    sub = RecordingSubscriber()
    bus.subscribe(sub)

    await bus.emit(_event())

    assert len(sub.received) == 1
    assert bus.subscribers == (sub,)


@pytest.mark.asyncio
async def test_subscriber_failure_is_non_blocking():
    failing = FailingSubscriber()
    healthy = RecordingSubscriber()
    bus = RuntimeEventBus([failing, healthy])

    await bus.emit(_event())  # must not raise despite failing subscriber

    assert failing.calls == 1
    assert len(healthy.received) == 1  # healthy still notified after failure


@pytest.mark.asyncio
async def test_subscribers_notified_in_registration_order():
    order: list[str] = []

    class Named:
        def __init__(self, name: str) -> None:
            self.name = name

        async def on_event(self, event: RuntimeEvent) -> None:
            order.append(self.name)

    bus = RuntimeEventBus([Named("first"), Named("second")])
    bus.subscribe(Named("third"))

    await bus.emit(_event())

    assert order == ["first", "second", "third"]


@pytest.mark.asyncio
async def test_emit_preserves_event_sequence():
    sub = RecordingSubscriber()
    bus = RuntimeEventBus([sub])

    sequence = [
        _event(EventType.RUN_STARTED),
        _event(EventType.ROUTE_SELECTED),
        _event(EventType.RUN_COMPLETED),
    ]
    for event in sequence:
        await bus.emit(event)

    assert [e.event_type for e in sub.received] == [
        EventType.RUN_STARTED,
        EventType.ROUTE_SELECTED,
        EventType.RUN_COMPLETED,
    ]


def test_event_bus_has_no_concrete_dependencies():
    source = inspect.getsource(event_bus_module)
    for marker in FORBIDDEN_IMPORT_MARKERS:
        assert marker not in source, f"event_bus must not depend on {marker}"
    # Depends only on contracts/events — never on a concrete subscriber package/class.
    assert "app.runtime.subscribers" not in source
    assert "AgentStepsSubscriber" not in source
    assert "LoggingSubscriber" not in source
