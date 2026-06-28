"""LoggingSubscriber — structured logging of every runtime event (M5.4C)."""

from __future__ import annotations

import logging

from app.runtime.events import RuntimeEvent

_DEFAULT_LOGGER = "app.runtime.events"


class LoggingSubscriber:
    """Logs every runtime event. Never raises (R6)."""

    def __init__(self, logger_name: str = _DEFAULT_LOGGER) -> None:
        self._logger = logging.getLogger(logger_name)

    async def on_event(self, event: RuntimeEvent) -> None:
        self._logger.info(
            "runtime_event type=%s run=%s corr=%s meta=%s",
            event.event_type.value,
            event.run_id,
            event.correlation_id,
            event.metadata,
        )
