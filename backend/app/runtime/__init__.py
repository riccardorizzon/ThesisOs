"""Runtime Platform — public runtime contracts + Event Bus (M5.4A–B).

Exposes the Runtime Event Contract (M5.4A) and the Runtime Event Bus (M5.4B).
Concrete subscribers and graph wiring arrive in M5.4C. Governed by the Runtime
Constitution (`docs/runtime-constitution.md`) and ADR-0030.
"""

from app.runtime.contracts import RuntimeEventEmitter, RuntimeSubscriber
from app.runtime.event_bus import RuntimeEventBus
from app.runtime.events import EVENT_VOCABULARY, EventType, RuntimeEvent

__all__ = [
    "EVENT_VOCABULARY",
    "EventType",
    "RuntimeEvent",
    "RuntimeEventBus",
    "RuntimeEventEmitter",
    "RuntimeSubscriber",
]
