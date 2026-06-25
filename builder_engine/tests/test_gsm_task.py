from __future__ import annotations

import pytest

from builder_engine.graph import BuilderGraph, Packet
from builder_engine.gsm_task import schedule_packet, sync_validate_outcome, transition
from builder_engine.state_machine import ExecutionState, TransitionError


def _graph(*packets: Packet) -> BuilderGraph:
    return BuilderGraph(
        path=__file__,
        epic="test",
        chain=None,
        status="active",
        wave=1,
        packets={p.id: p for p in packets},
    )


def test_happy_path_t01_through_t06():
    state = ExecutionState.CREATED
    state = transition(state, "prepare")
    assert state == ExecutionState.READY
    g = _graph(Packet("P1", 1, "explorer", "ready", (), ("docs/",)))
    state = schedule_packet(g, "P1", current=state)
    assert state == ExecutionState.RUNNING
    state = sync_validate_outcome(state, checks_passed=True)
    assert state == ExecutionState.DONE


def test_t07_failure_recovery_t08_t09():
    state = ExecutionState.RUNNING
    state = sync_validate_outcome(state, checks_passed=False)
    assert state == ExecutionState.FAILED
    state = transition(state, "debug")
    assert state == ExecutionState.DEBUGGING
    state = transition(state, "retry")
    assert state == ExecutionState.READY


def test_t11_timeout():
    state = transition(ExecutionState.RUNNING, "timeout")
    assert state == ExecutionState.FAILED


def test_t12_abort_claim():
    g = _graph(Packet("P1", 1, "explorer", "ready", (), ("docs/",)))
    state = transition(ExecutionState.READY, "claim", graph=g, packet_id="P1")
    state = transition(state, "abort_claim")
    assert state == ExecutionState.READY


def test_inv_a1_validate_not_from_running():
    with pytest.raises(TransitionError, match="INV-A1"):
        transition(ExecutionState.READY, "validate")


def test_inv_a3_terminal_done():
    with pytest.raises(TransitionError, match="INV-A3"):
        transition(ExecutionState.DONE, "claim")


def test_inv_a4_retry_only_from_debugging():
    with pytest.raises(TransitionError, match="INV-A4"):
        transition(ExecutionState.FAILED, "retry")


def test_inv_a5_dependency_not_done():
    g = _graph(
        Packet("P1", 1, "explorer", "ready", ("P0",), ("docs/",)),
        Packet("P0", 1, "explorer", "ready", (), ("other/",)),
    )
    with pytest.raises(TransitionError, match="INV-A5"):
        schedule_packet(g, "P1", current=ExecutionState.READY)


def test_illegal_transition_raises():
    with pytest.raises(TransitionError, match="illegal transition"):
        transition(ExecutionState.CREATED, "claim")
