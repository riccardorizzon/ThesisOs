"""L2 Global State Machine — Task entity transitions (ADR-0025 + L2 §5.5)."""

from __future__ import annotations

from builder_engine.graph import BuilderGraph, Packet
from builder_engine.state_machine import ExecutionState, TransitionError

_TRANSITIONS: dict[tuple[ExecutionState, str], ExecutionState] = {
    (ExecutionState.CREATED, "prepare"): ExecutionState.READY,
    (ExecutionState.READY, "claim"): ExecutionState.CLAIMED,
    (ExecutionState.CLAIMED, "start"): ExecutionState.RUNNING,
    (ExecutionState.RUNNING, "validate"): ExecutionState.VALIDATING,
    (ExecutionState.VALIDATING, "pass"): ExecutionState.MERGED,
    (ExecutionState.MERGED, "complete"): ExecutionState.DONE,
    (ExecutionState.VALIDATING, "fail"): ExecutionState.FAILED,
    (ExecutionState.FAILED, "debug"): ExecutionState.DEBUGGING,
    (ExecutionState.DEBUGGING, "retry"): ExecutionState.READY,
    (ExecutionState.READY, "cancel"): ExecutionState.CANCELLED,
    (ExecutionState.RUNNING, "timeout"): ExecutionState.FAILED,
    (ExecutionState.CLAIMED, "abort_claim"): ExecutionState.READY,
}

_TERMINAL: frozenset[ExecutionState] = frozenset({ExecutionState.DONE, ExecutionState.CANCELLED})


def _deps_satisfied(graph: BuilderGraph, packet: Packet) -> bool:
    for dep_id in packet.depends_on:
        dep = graph.packets.get(dep_id)
        if dep is None or dep.status != "done":
            return False
    return True


def _assert_class_a(
    current: ExecutionState,
    event: str,
    *,
    graph: BuilderGraph | None,
    packet_id: str | None,
) -> None:
    """INV-A1–A5 guards (L1 Class A, L2 §8)."""
    if current in _TERMINAL:
        raise TransitionError(f"INV-A3: terminal state {current.value} cannot transition")

    if event == "validate" and current != ExecutionState.RUNNING:
        raise TransitionError(f"INV-A1: validate requires RUNNING, got {current.value}")

    if event == "fail" and current != ExecutionState.VALIDATING:
        raise TransitionError(f"INV-A1: fail requires VALIDATING, got {current.value}")

    if event == "pass" and current != ExecutionState.VALIDATING:
        raise TransitionError(f"INV-A2: pass requires VALIDATING, got {current.value}")

    if event == "complete" and current != ExecutionState.MERGED:
        raise TransitionError(f"INV-A2: complete requires MERGED, got {current.value}")

    if event == "retry" and current != ExecutionState.DEBUGGING:
        raise TransitionError(f"INV-A4: retry requires DEBUGGING, got {current.value}")

    if event in ("claim", "start") and graph is not None and packet_id is not None:
        packet = graph.packets.get(packet_id)
        if packet is None:
            raise TransitionError(f"unknown packet: {packet_id}")
        if not _deps_satisfied(graph, packet):
            raise TransitionError(f"INV-A5: {packet_id} dependencies not done")


def transition(
    current: ExecutionState,
    event: str,
    *,
    graph: BuilderGraph | None = None,
    packet_id: str | None = None,
) -> ExecutionState:
    """Apply a legal Task transition with Class A invariant guards."""
    _assert_class_a(current, event, graph=graph, packet_id=packet_id)
    key = (current, event)
    if key not in _TRANSITIONS:
        raise TransitionError(f"illegal transition: {current.value} --{event}--> ?")
    return _TRANSITIONS[key]


def schedule_packet(graph: BuilderGraph, packet_id: str, *, current: ExecutionState) -> ExecutionState:
    """T-02 claim + T-03 start (Scheduling / Claiming behaviors)."""
    state = transition(current, "claim", graph=graph, packet_id=packet_id)
    return transition(state, "start", graph=graph, packet_id=packet_id)


def sync_validate_outcome(
    current: ExecutionState,
    *,
    checks_passed: bool,
) -> ExecutionState:
    """T-04 validate → T-05 pass → T-06 complete, or T-07 fail."""
    state = transition(current, "validate")
    if checks_passed:
        state = transition(state, "pass")
        return transition(state, "complete")
    return transition(state, "fail")
