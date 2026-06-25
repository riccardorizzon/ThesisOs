"""Formal execution state machine for build-time packets (ADR-0025, L2 §5.5)."""

from __future__ import annotations

from enum import Enum

from builder_engine import gsm_task
from builder_engine.graph import BuilderGraph


class ExecutionState(str, Enum):
    CREATED = "created"
    READY = "ready"
    CLAIMED = "claimed"
    RUNNING = "running"
    VALIDATING = "validating"
    MERGED = "merged"
    DONE = "done"
    FAILED = "failed"
    DEBUGGING = "debugging"
    CANCELLED = "cancelled"


class TransitionError(ValueError):
    """Illegal state transition."""


# STATE.yaml packet status ↔ runtime execution state (ADR-0025 §3)
YAML_STATUS_TO_EXECUTION: dict[str, ExecutionState] = {
    "ready": ExecutionState.READY,
    "in_progress": ExecutionState.RUNNING,
    "done": ExecutionState.DONE,
    "blocked": ExecutionState.DEBUGGING,
    "cancelled": ExecutionState.CANCELLED,
}

EXECUTION_TO_YAML_STATUS: dict[ExecutionState, str] = {
    ExecutionState.CREATED: "ready",
    ExecutionState.READY: "ready",
    ExecutionState.CLAIMED: "in_progress",
    ExecutionState.RUNNING: "in_progress",
    ExecutionState.VALIDATING: "in_progress",
    ExecutionState.MERGED: "in_progress",
    ExecutionState.DONE: "done",
    ExecutionState.FAILED: "blocked",
    ExecutionState.DEBUGGING: "blocked",
    ExecutionState.CANCELLED: "cancelled",
}


def execution_from_yaml_status(status: str) -> ExecutionState:
    try:
        return YAML_STATUS_TO_EXECUTION[status]
    except KeyError as exc:
        raise TransitionError(f"unknown packet status: {status}") from exc


def yaml_status_from_execution(state: ExecutionState) -> str:
    return EXECUTION_TO_YAML_STATUS[state]


def transition(
    current: ExecutionState,
    event: str,
    *,
    graph: BuilderGraph | None = None,
    packet_id: str | None = None,
) -> ExecutionState:
    return gsm_task.transition(current, event, graph=graph, packet_id=packet_id)
