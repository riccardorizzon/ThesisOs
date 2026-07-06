"""MB2-Q3 — Scheduler qualification tests (normative test IDs).

SoR §13.2 MB2-Q3: claim/release; lock acquisition; respects WAIT;
MB2-Q-007…009. Evidence on EWO-005 — no new implementation.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from builder_engine.dependency import DependencyEngine
from builder_engine.events import BuildEventBus
from builder_engine.graph import BuilderGraph, Packet
from builder_engine.job_queue import JobQueue
from builder_engine.program_graph import load_program_graph
from builder_engine.scheduler import (
    SchedulerHaltedError,
    SchedulerPlugin,
    SupervisorGate,
    file_locks_for_packet,
)
from builder_engine.state_machine import ExecutionState, TransitionError


def _fixtures_dir() -> Path:
    return Path(__file__).resolve().parent / "fixtures"


def _minimal_program():
    return load_program_graph(_fixtures_dir() / "px_exec_program_minimal.yaml")


def _materialized_queue(tmp_path: Path) -> tuple[JobQueue, BuildEventBus]:
    program = _minimal_program()
    bus = BuildEventBus(tmp_path)
    engine = DependencyEngine(program)
    graph = engine.derive(publish=False)
    queue = JobQueue(bus=bus, cycle_id="mb2-q3")
    queue.materialize(engine, graph)
    return queue, bus


def _builder_graph() -> BuilderGraph:
    return BuilderGraph(
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


def _lock_graph() -> BuilderGraph:
    return BuilderGraph(
        path=__file__,
        epic="test",
        chain=None,
        status="active",
        wave=1,
        packets={
            "A": Packet("A", 1, "implementer", "ready", (), ("backend/app/",)),
            "B": Packet("B", 1, "implementer", "ready", (), ("backend/app/services/",)),
        },
    )


def test_mb2_q_007_single_flight_lock_per_job(tmp_path):
    """§8.2: one claim per job until release (Phase 1 job-level single-flight)."""
    queue, bus = _materialized_queue(tmp_path)
    scheduler = SchedulerPlugin(queue)
    graph = _builder_graph()

    job_id = "PX-EXEC-EWO-003"
    scheduler.claim(job_id, graph=graph)
    assert queue.get(job_id).state == ExecutionState.CLAIMED
    assert job_id not in queue.ready_queue()

    with pytest.raises(TransitionError, match="illegal transition"):
        scheduler.claim(job_id, graph=graph)

    claimed_events = [e for e in bus.replay() if e.type == "JobClaimed"]
    assert len(claimed_events) == 1

    locks_a = file_locks_for_packet(_lock_graph().packets["A"])
    locks_b = file_locks_for_packet(_lock_graph().packets["B"])
    assert locks_a.keys().isdisjoint(locks_b.keys())


def test_mb2_q_007_claim_next_single_flight(tmp_path):
    queue, _bus = _materialized_queue(tmp_path)
    scheduler = SchedulerPlugin(queue)
    graph = _builder_graph()

    claimed = scheduler.claim_next(max_claims=1, graph=graph)
    assert len(claimed) == 1
    assert claimed[0].state == ExecutionState.CLAIMED
    assert len(queue.ready_queue()) == 1


def test_mb2_q_008_supervisor_wait_halts_new_claims(tmp_path):
    """INV-R-16: WAIT halts claim (REQ-12)."""
    queue, bus = _materialized_queue(tmp_path)
    scheduler = SchedulerPlugin(queue, supervisor=SupervisorGate.WAIT)
    graph = _builder_graph()

    with pytest.raises(SchedulerHaltedError, match="claim refused"):
        scheduler.claim("PX-EXEC-EWO-003", graph=graph)

    with pytest.raises(SchedulerHaltedError, match="refused"):
        scheduler.claim_next(max_claims=1, graph=graph)

    assert queue.get("PX-EXEC-EWO-003").state == ExecutionState.READY
    assert not [e for e in bus.replay() if e.type == "JobClaimed"]


def test_mb2_q_009_dispatch_manifest_emitted_on_claim(tmp_path):
    """§6.3 / §8.2: manifest persisted after claim workflow."""
    queue, bus = _materialized_queue(tmp_path)
    scheduler = SchedulerPlugin(queue)
    graph = _builder_graph()
    fixed_ts = "2026-07-06T00:00:00+00:00"

    claimed = scheduler.claim("PX-EXEC-EWO-003", graph=graph)
    manifest = scheduler.build_manifest([claimed.job_id], generated_at=fixed_ts)

    assert manifest.manifest_path.is_file()
    on_disk = json.loads(manifest.manifest_path.read_text(encoding="utf-8"))
    assert on_disk["program_id"] == "px-exec-test"
    assert on_disk["generated_at"] == fixed_ts
    assert on_disk["entries"][0]["job_id"] == "PX-EXEC-EWO-003"
    assert on_disk["entries"][0]["state"] == "claimed"

    claimed_events = [e for e in bus.replay() if e.type == "JobClaimed"]
    assert len(claimed_events) == 1
    assert claimed_events[0].payload["ewo_id"] == "PX-EXEC-EWO-003"


def test_mb2_q_009_claim_next_manifest_sequence(tmp_path):
    queue, bus = _materialized_queue(tmp_path)
    scheduler = SchedulerPlugin(queue)
    graph = _builder_graph()
    fixed_ts = "2026-07-06T00:00:00+00:00"

    claimed = scheduler.claim_next(max_claims=2, graph=graph)
    manifest = scheduler.build_manifest([j.job_id for j in claimed], generated_at=fixed_ts)

    assert len(manifest.entries) == 2
    assert [e.job_id for e in manifest.entries] == ["PX-EXEC-EWO-002", "PX-EXEC-EWO-003"]
    assert len([e for e in bus.replay() if e.type == "JobClaimed"]) == 2
