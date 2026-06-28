"""Runtime Event Bus (M5.4B) — fan-out of runtime events to subscribers.

Implements :class:`~app.runtime.contracts.RuntimeEventEmitter`. Depends only on the
runtime contracts (events + Protocols) — never on a concrete subscriber
(Constitution C4; ADR-0030 R6/R8). Properties:

- A bus with **zero subscribers is valid and silent** (``emit`` is a no-op).
- Subscribers are notified **in registration order** (deterministic).
- A subscriber failure is **swallowed and logged** so a faulty subscriber can never
  break a user-visible turn (R6).

No dispatch to concrete subscribers, persistence, or graph wiring lives here.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable

from app.runtime.contracts import RuntimeSubscriber
from app.runtime.events import RuntimeEvent

logger = logging.getLogger("app.runtime.event_bus")


class RuntimeEventBus:
    """Dispatches :class:`RuntimeEvent` instances to registered subscribers."""

    def __init__(self, subscribers: Iterable[RuntimeSubscriber] | None = None) -> None:
        self._subscribers: list[RuntimeSubscriber] = list(subscribers or ())

    def subscribe(self, subscriber: RuntimeSubscriber) -> None:
        """Register a subscriber. Composition root only (ADR-0030 C2/R2)."""
        self._subscribers.append(subscriber)

    @property
    def subscribers(self) -> tuple[RuntimeSubscriber, ...]:
        return tuple(self._subscribers)

    async def emit(self, event: RuntimeEvent) -> None:
        """Notify every subscriber, in order. Subscriber errors never propagate (R6)."""
        for subscriber in self._subscribers:
            try:
                await subscriber.on_event(event)
            except Exception:  # noqa: BLE001 — R6: a subscriber must never break the turn
                logger.exception(
                    "runtime subscriber %s failed handling %s",
                    type(subscriber).__name__,
                    event.event_type.value,
                )
