"""Runtime event emission helpers (M5.4C).

The **Runtime** wraps Business graph nodes here to emit canonical events at
lifecycle boundaries. Business agents never import this module — emission is a
Runtime concern (Constitution C3/C4; ADR-0030 R8).

`emit_safely` guarantees emission never breaks a turn: failures are swallowed and
logged (the Event Bus also isolates subscriber failures — R6).
"""

from __future__ import annotations

import functools
import logging
from collections.abc import Awaitable, Callable
from time import perf_counter

from app.runtime.contracts import RuntimeEventEmitter
from app.runtime.events import EventType, RuntimeEvent

logger = logging.getLogger("app.runtime.instrumentation")

NodeFn = Callable[..., Awaitable[dict]]


async def emit_safely(emitter: RuntimeEventEmitter, event: RuntimeEvent) -> None:
    """Emit an event; never propagate a failure into the turn."""
    try:
        await emitter.emit(event)
    except Exception:  # noqa: BLE001 — emission must never break the turn
        logger.exception("event emission failed for %s", event.event_type.value)


def make_event(
    event_type: EventType, *, run_id: str, correlation_id: str | None, **metadata
) -> RuntimeEvent:
    return RuntimeEvent(
        event_type=event_type,
        run_id=run_id,
        correlation_id=correlation_id,
        metadata=metadata,
    )


def _elapsed_ms(start: float) -> float:
    return round((perf_counter() - start) * 1000, 3)


def instrument_node(
    node_fn: NodeFn,
    *,
    emitter: RuntimeEventEmitter,
    run_id: str,
    correlation_id: str | None,
    agent: str,
    phase: str,
    route_event: bool = False,
) -> NodeFn:
    """Wrap a Business node so the Runtime emits NodeStarted / NodeCompleted /
    NodeFailed (and RouteSelected for the router). The node body is untouched.

    `functools.wraps` keeps the wrapped node's signature visible so LangGraph still
    injects `config`/`store`/`writer` when the original node declares them."""

    @functools.wraps(node_fn)
    async def wrapped(*args, **kwargs):
        await emit_safely(
            emitter, make_event(EventType.NODE_STARTED, run_id=run_id, correlation_id=correlation_id, agent=agent, phase=phase)
        )
        start = perf_counter()
        try:
            result = await node_fn(*args, **kwargs)
        except Exception as exc:
            await emit_safely(
                emitter,
                make_event(
                    EventType.NODE_FAILED, run_id=run_id, correlation_id=correlation_id,
                    agent=agent, phase=phase, error=str(exc), duration_ms=_elapsed_ms(start),
                ),
            )
            raise
        await emit_safely(
            emitter,
            make_event(
                EventType.NODE_COMPLETED, run_id=run_id, correlation_id=correlation_id,
                agent=agent, phase=phase, duration_ms=_elapsed_ms(start),
            ),
        )
        if route_event and isinstance(result, dict) and result.get("route"):
            await emit_safely(
                emitter,
                make_event(EventType.ROUTE_SELECTED, run_id=run_id, correlation_id=correlation_id, route=result["route"]),
            )
        return result

    return wrapped
