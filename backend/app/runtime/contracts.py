"""Runtime interfaces for the future Event Bus (M5.4A).

Defines the public Protocols the Runtime Event Bus (M5.4B) will use, without any
dispatch logic or concrete implementation:

- :class:`RuntimeSubscriber` — consumer contract; the Runtime notifies subscribers
  of events without knowing concrete implementations (Constitution C4; ADR-0030 R6/R8).
- :class:`RuntimeEventEmitter` — producer contract; Runtime composition emits events
  through this interface. The future Event Bus implements it and fans out to
  subscribers. The bus depends only on these Protocols, never on concrete subscribers.

Runtime Layer only — no LangGraph, DB, LLM, or Business imports.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.runtime.events import RuntimeEvent


@runtime_checkable
class RuntimeSubscriber(Protocol):
    """Minimal subscriber contract. Implementations must be non-blocking with respect
    to the user-visible turn: a subscriber failure must never fail a run (ADR-0030 R6)."""

    async def on_event(self, event: RuntimeEvent) -> None:
        """Handle a single runtime event. Implementations must not raise into the caller."""
        ...


@runtime_checkable
class RuntimeEventEmitter(Protocol):
    """Producer contract used by Runtime composition to publish events. The future
    Event Bus implements this and dispatches to registered subscribers."""

    async def emit(self, event: RuntimeEvent) -> None:
        """Publish a runtime event to all registered subscribers."""
        ...
