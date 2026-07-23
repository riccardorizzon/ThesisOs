"""In-process event dispatcher with outbox persistence (ADR-0006).

Producers call ``publish``; events are appended to the ``events`` table in the
same transaction when a session is supplied (preferred). A standalone session is
opened only for ad-hoc publishes outside a service transaction.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.db.session_async import AsyncSessionLocal
from app.services.project_scope import resolve_project_id

_CATALOG_PATH = (
    Path(__file__).resolve().parents[4] / "contracts" / "events" / "events.json"
)


class UnknownEventError(ValueError):
    """Raised when ``event_name`` is not in the frozen event catalog."""


@lru_cache(maxsize=1)
def _catalog_event_names() -> frozenset[str]:
    data = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))
    return frozenset(e["name"] for e in data["events"])


async def publish(
    event_name: str,
    payload: dict,
    *,
    session: AsyncSession | None = None,
    source: str | None = None,
    correlation_id: str | None = None,
    project_id: str | None = None,
) -> models.Event:
    """Persist a catalog event to the outbox table."""
    if event_name not in _catalog_event_names():
        raise UnknownEventError(f"unknown event: {event_name}")

    row = models.Event(
        type=event_name,
        payload=payload,
        source=source,
        correlation_id=correlation_id,
        project_id=resolve_project_id(project_id),
    )
    if session is not None:
        session.add(row)
        await session.flush()
        return row

    async with AsyncSessionLocal() as s:
        try:
            s.add(row)
            await s.commit()
            return row
        except Exception:
            await s.rollback()
            raise
