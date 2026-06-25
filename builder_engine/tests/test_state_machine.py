from __future__ import annotations

import pytest

from builder_engine.state_machine import (
    ExecutionState,
    TransitionError,
    execution_from_yaml_status,
    transition,
    yaml_status_from_execution,
)


def test_happy_path_transitions():
    state = ExecutionState.CREATED
    state = transition(state, "prepare")
    assert state == ExecutionState.READY
    state = transition(state, "claim")
    assert state == ExecutionState.CLAIMED
    state = transition(state, "start")
    assert state == ExecutionState.RUNNING
    state = transition(state, "validate")
    assert state == ExecutionState.VALIDATING
    state = transition(state, "pass")
    assert state == ExecutionState.MERGED
    state = transition(state, "complete")
    assert state == ExecutionState.DONE


def test_failure_recovery_loop():
    state = ExecutionState.RUNNING
    state = transition(state, "validate")
    state = transition(state, "fail")
    assert state == ExecutionState.FAILED
    state = transition(state, "debug")
    assert state == ExecutionState.DEBUGGING
    state = transition(state, "retry")
    assert state == ExecutionState.READY


def test_illegal_transition_raises():
    with pytest.raises(TransitionError, match="INV-A3"):
        transition(ExecutionState.DONE, "claim")


@pytest.mark.parametrize(
    ("yaml_status", "expected"),
    [
        ("ready", ExecutionState.READY),
        ("in_progress", ExecutionState.RUNNING),
        ("done", ExecutionState.DONE),
        ("blocked", ExecutionState.DEBUGGING),
        ("cancelled", ExecutionState.CANCELLED),
    ],
)
def test_yaml_status_roundtrip(yaml_status: str, expected: ExecutionState):
    assert execution_from_yaml_status(yaml_status) == expected
    assert yaml_status_from_execution(expected) in (yaml_status, "ready", "in_progress")
