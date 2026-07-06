from __future__ import annotations

from pathlib import Path

import pytest

from builder_engine.dependency import DependencyEngine
from builder_engine.events import BuildEventBus
from builder_engine.graph import BuilderGraph, Packet
from builder_engine.job_queue import Job, JobQueue, job_transition
from builder_engine.program_graph import load_program_graph
from builder_engine.state_machine import ExecutionState, TransitionError


def _fixtures_dir() -> Path:
    return Path(__file__).resolve().parent / "fixtures"


def _minimal_program():
    return load_program_graph(_fixtures_dir() / "px_exec_program_minimal.yaml")


def test_job_fsm_happy_path():
    job = Job(
        job_id="PX-EXEC-EWO-002",
        program_id="px-exec-test",
        ewo_id="PX-EXEC-EWO-002",
        state=ExecutionState.CREATED,
    )
    job_transition(job, "prepare")
    assert job.state == ExecutionState.READY
    job_transition(job, "claim")
    assert job.state == ExecutionState.CLAIMED
    job_transition(job, "start")
    assert job.state == ExecutionState.RUNNING
    job_transition(job, "validate")
    assert job.state == ExecutionState.VALIDATING
    job_transition(job, "pass")
    assert job.state == ExecutionState.MERGED
    job_transition(job, "complete")
    assert job.state == ExecutionState.DONE


def test_illegal_transition_raises():
    job = Job(
        job_id="j1",
        program_id="px-exec-test",
        ewo_id="PX-EXEC-EWO-002",
        state=ExecutionState.DONE,
    )
    with pytest.raises(TransitionError, match="INV-A3"):
        job_transition(job, "claim")


def test_illegal_transition_emits_runtime_escalated(tmp_path):
    bus = BuildEventBus(tmp_path)
    job = Job(
        job_id="j1",
        program_id="px-exec-test",
        ewo_id="PX-EXEC-EWO-002",
        state=ExecutionState.DONE,
    )
    with pytest.raises(TransitionError):
        job_transition(job, "claim", bus=bus, cycle_id="esc-cycle")
    events = bus.tail(1)
    assert len(events) == 1
    assert events[0].type == "RuntimeEscalated"
    assert events[0].payload["ewo_id"] == "PX-EXEC-EWO-002"
    assert events[0].payload["event"] == "claim"


def test_job_ready_and_claimed_events(tmp_path):
    bus = BuildEventBus(tmp_path)
    job = Job(
        job_id="PX-EXEC-EWO-003",
        program_id="px-exec-test",
        ewo_id="PX-EXEC-EWO-003",
        state=ExecutionState.CREATED,
    )
    job_transition(job, "prepare", bus=bus, cycle_id="evt-cycle")
    job_transition(job, "claim", bus=bus, cycle_id="evt-cycle")

    types = [e.type for e in bus.replay()]
    assert types.count("JobReady") == 1
    assert types.count("JobClaimed") == 1

    ready = next(e for e in bus.replay() if e.type == "JobReady")
    claimed = next(e for e in bus.replay() if e.type == "JobClaimed")
    assert ready.payload["job_id"] == "PX-EXEC-EWO-003"
    assert claimed.payload["state"] == "claimed"


def test_materialize_from_execution_graph(tmp_path):
    program = _minimal_program()
    bus = BuildEventBus(tmp_path)
    engine = DependencyEngine(program)
    graph = engine.derive(publish=False)
    queue = JobQueue(bus=bus, cycle_id="mat-cycle")

    jobs = queue.materialize(engine, graph)
    assert len(jobs) == 4

    ready = queue.list_jobs(state=ExecutionState.READY)
    ready_ids = [j.ewo_id for j in ready]
    assert ready_ids == ["PX-EXEC-EWO-003", "PX-EXEC-EWO-002"]

    done = queue.list_jobs(state=ExecutionState.DONE)
    assert {j.ewo_id for j in done} == {"PX-EXEC-EWO-001"}

    debugging = queue.list_jobs(state=ExecutionState.DEBUGGING)
    assert {j.ewo_id for j in debugging} == {"PX-EXEC-EWO-004"}

    assert queue.ready_queue() == ["PX-EXEC-EWO-003", "PX-EXEC-EWO-002"]

    ready_events = [e for e in bus.replay() if e.type == "JobReady"]
    assert len(ready_events) == 2
    assert {e.payload["ewo_id"] for e in ready_events} == {
        "PX-EXEC-EWO-002",
        "PX-EXEC-EWO-003",
    }


def test_claim_and_release(tmp_path):
    program = _minimal_program()
    bus = BuildEventBus(tmp_path)
    engine = DependencyEngine(program)
    graph = engine.derive(publish=False)
    queue = JobQueue(bus=bus, cycle_id="cl-cycle")
    queue.materialize(engine, graph)

    g = BuilderGraph(
        path=__file__,
        epic="test",
        chain=None,
        status="active",
        wave=1,
        packets={
            p.id: p
            for p in (
                Packet("PX-EXEC-EWO-001", 1, "explorer", "done", (), ()),
                Packet("PX-EXEC-EWO-002", 1, "explorer", "ready", ("PX-EXEC-EWO-001",), ()),
                Packet("PX-EXEC-EWO-003", 1, "explorer", "ready", ("PX-EXEC-EWO-001",), ()),
            )
        },
    )

    claimed = queue.claim("PX-EXEC-EWO-003", graph=g)
    assert claimed.state == ExecutionState.CLAIMED
    assert "PX-EXEC-EWO-003" not in queue.ready_queue()

    claimed_events = [e for e in bus.replay() if e.type == "JobClaimed"]
    assert len(claimed_events) == 1
    assert claimed_events[0].payload["ewo_id"] == "PX-EXEC-EWO-003"

    released = queue.release("PX-EXEC-EWO-003", graph=g)
    assert released.state == ExecutionState.READY
    assert "PX-EXEC-EWO-003" in queue.ready_queue()


def test_materialize_ready_subset(tmp_path):
    program = _minimal_program()
    bus = BuildEventBus(tmp_path)
    engine = DependencyEngine(program)
    graph = engine.derive(publish=False)
    queue = JobQueue(bus=bus)

    ready_jobs = queue.materialize_ready(engine, graph)
    assert len(ready_jobs) == 2
    assert [j.ewo_id for j in ready_jobs] == ["PX-EXEC-EWO-003", "PX-EXEC-EWO-002"]
    assert len(queue.list_jobs()) == 2


def test_enqueue_requires_ready():
    queue = JobQueue()
    job = Job(
        job_id="j1",
        program_id="px-exec-test",
        ewo_id="PX-EXEC-EWO-004",
        state=ExecutionState.CREATED,
    )
    with pytest.raises(TransitionError, match="enqueue requires READY"):
        queue.enqueue(job)
