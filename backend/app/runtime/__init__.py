"""Runtime Platform — public runtime contracts (M5.4A).

Currently exposes the Runtime Event Contract only. The Event Bus, dispatch, and
concrete subscribers arrive in M5.4B. Governed by the Runtime Constitution
(`docs/runtime-constitution.md`) and ADR-0030.
"""

from app.runtime.contracts import RuntimeEventEmitter, RuntimeSubscriber
from app.runtime.events import EVENT_VOCABULARY, EventType, RuntimeEvent

__all__ = [
    "EVENT_VOCABULARY",
    "EventType",
    "RuntimeEvent",
    "RuntimeEventEmitter",
    "RuntimeSubscriber",
]
