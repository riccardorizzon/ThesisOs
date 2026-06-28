"""AgentStepsSubscriber — persists one agent_steps row per node execution (M5.4C)."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from app.db import models
from app.db.session_async import AsyncSessionLocal
from app.runtime.events import EventType, RuntimeEvent

logger = logging.getLogger("app.runtime.subscribers.agent_steps")

_TERMINAL_STATUS = {
    EventType.NODE_COMPLETED: "done",
    EventType.NODE_FAILED: "error",
}


class AgentStepsSubscriber:
    """Writes an `agent_steps` row on each node terminal event, linked to
    `agent_run_id` (= event.run_id). Run-level and routing events are ignored here
    (recorded on `agent_runs` / handled by other subscribers)."""

    async def on_event(self, event: RuntimeEvent) -> None:
        status = _TERMINAL_STATUS.get(event.event_type)
        if status is None:
            return
        try:
            await self._persist(event, status)
        except Exception:  # noqa: BLE001 — subscriber must never raise into the bus (R6)
            logger.exception("failed to persist agent_step for run %s", event.run_id)

    async def _persist(self, event: RuntimeEvent, status: str) -> None:
        md = event.metadata
        now = datetime.now(timezone.utc)
        duration = md.get("duration_ms")
        started = now - timedelta(milliseconds=duration) if isinstance(duration, (int, float)) else now
        output = {k: v for k, v in md.items() if k not in ("agent", "phase")}
        async with AsyncSessionLocal() as session:
            session.add(
                models.AgentStep(
                    agent_run_id=event.run_id,
                    agent=md.get("agent"),
                    phase=md.get("phase"),
                    input={},
                    output=output,
                    status=status,
                    started_at=started,
                    finished_at=now,
                )
            )
            await session.commit()
