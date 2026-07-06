from __future__ import annotations

import json
from pathlib import Path

import pytest

from builder_engine.dependency import DependencyEngine
from builder_engine.events import BuildEventBus
from builder_engine.graph import BuilderGraph, Packet
from builder_engine.job_queue import JobQueue
from builder_engine.program_graph import load_program_graph
from builder_engine.rules import ActionDescriptor
from builder_engine.scheduler import (
    SchedulerHaltedError,
    SchedulerPlugin,
    SupervisorGate,
    compute_ready,
)
from builder_engine.state_machine import ExecutionState


def _fixtures_dir() -> Path:
    return Path(__file__).resolve().parent / "fixtures"


def _minimal_program():
    return load_program_graph(_fixtures_dir() / "px_exec_program_minimal.yaml")


def _materialized_queue(tmp_path: Path) -> tuple[JobQueue, BuildEventBus]:
    program = _minimal_program()
    bus = BuildEventBus(tmp_path)
    engine = DependencyEngine(program)
    graph = engine.derive(publish=False)
    queue = JobQueue(bus=bus, cycle_id="sched-cycle")
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


def test_scheduler_claim_delegates_to_queue(tmp_path):
    queue, bus = _materialized_queue(tmp_path)
    scheduler = SchedulerPlugin(queue)
    graph = _builder_graph()

    claimed = scheduler.claim("PX-EXEC-EWO-003", graph=graph)

    assert claimed.state == ExecutionState.CLAIMED
    assert "PX-EXEC-EWO-003" not in queue.ready_queue()
    claimed_events = [e for e in bus.replay() if e.type == "JobClaimed"]
    assert len(claimed_events) == 1
    assert claimed_events[0].payload["ewo_id"] == "PX-EXEC-EWO-003"


def test_scheduler_wait_halts_claim(tmp_path):
    queue, bus = _materialized_queue(tmp_path)
    scheduler = SchedulerPlugin(queue, supervisor=SupervisorGate.WAIT)
    graph = _builder_graph()

    with pytest.raises(SchedulerHaltedError, match="claim refused"):
        scheduler.claim("PX-EXEC-EWO-003", graph=graph)

    assert queue.get("PX-EXEC-EWO-003").state == ExecutionState.READY
    assert "PX-EXEC-EWO-003" in queue.ready_queue()
    assert not [e for e in bus.replay() if e.type == "JobClaimed"]


def test_scheduler_stop_halts_claim(tmp_path):
    queue, bus = _materialized_queue(tmp_path)
    scheduler = SchedulerPlugin(queue, supervisor=SupervisorGate.STOP)
    graph = _builder_graph()

    with pytest.raises(SchedulerHaltedError, match="claim refused"):
        scheduler.claim("PX-EXEC-EWO-002", graph=graph)

    assert not [e for e in bus.replay() if e.type == "JobClaimed"]


def test_build_manifest_deterministic(tmp_path):
    queue, _bus = _materialized_queue(tmp_path)
    scheduler = SchedulerPlugin(queue)
    job_ids = ["PX-EXEC-EWO-002", "PX-EXEC-EWO-003"]
    fixed_ts = "2026-07-06T00:00:00+00:00"

    first = scheduler.build_manifest(job_ids, generated_at=fixed_ts)
    second = scheduler.build_manifest(job_ids, generated_at=fixed_ts)

    body_first = {k: v for k, v in first.to_dict().items() if k != "manifest_path"}
    body_second = {k: v for k, v in second.to_dict().items() if k != "manifest_path"}
    assert body_first == body_second
    assert [e["job_id"] for e in body_first["entries"]] == [
        "PX-EXEC-EWO-002",
        "PX-EXEC-EWO-003",
    ]
    assert first.manifest_path.is_file()
    on_disk = json.loads(first.manifest_path.read_text(encoding="utf-8"))
    assert on_disk["program_id"] == "px-exec-test"
    assert on_disk["generated_at"] == fixed_ts


def test_claim_next_respects_queue_order(tmp_path):
    queue, bus = _materialized_queue(tmp_path)
    scheduler = SchedulerPlugin(queue)
    graph = _builder_graph()

    assert queue.ready_queue() == ["PX-EXEC-EWO-003", "PX-EXEC-EWO-002"]

    claimed = scheduler.claim_next(max_claims=2, graph=graph)

    assert [j.ewo_id for j in claimed] == ["PX-EXEC-EWO-003", "PX-EXEC-EWO-002"]
    assert all(j.state == ExecutionState.CLAIMED for j in claimed)
    assert len([e for e in bus.replay() if e.type == "JobClaimed"]) == 2


def test_release_returns_job_to_ready(tmp_path):
    queue, _bus = _materialized_queue(tmp_path)
    scheduler = SchedulerPlugin(queue)
    graph = _builder_graph()

    scheduler.claim("PX-EXEC-EWO-003", graph=graph)
    assert "PX-EXEC-EWO-003" not in queue.ready_queue()

    released = scheduler.release("PX-EXEC-EWO-003", graph=graph)

    assert released.state == ExecutionState.READY
    assert "PX-EXEC-EWO-003" in queue.ready_queue()


def test_era_compute_ready_unchanged():
    repo_root = Path(__file__).resolve().parents[2]
    graph = BuilderGraph.load(repo_root / "plans" / "builder" / "STATE.example.yaml")
    ready = compute_ready(graph)
    assert {p.id for p in ready} == {"P1", "P2", "P3"}


def test_on_action_stub_no_claim(tmp_path, caplog):
    queue, bus = _materialized_queue(tmp_path)
    scheduler = SchedulerPlugin(queue)
    initial_ready = list(queue.ready_queue())

    descriptor = ActionDescriptor(
        plugin="scheduler",
        params={"job_id": "PX-EXEC-EWO-003"},
        rule_id="rule-claim",
        matched_event_id="JobReady@t@cycle",
    )
    with caplog.at_level("INFO"):
        scheduler.on_action(descriptor)

    assert queue.ready_queue() == initial_ready
    assert not [e for e in bus.replay() if e.type == "JobClaimed"]
    assert "on_action stub" in caplog.text


def test_supervisor_gate_default_execute(tmp_path):
    queue, bus = _materialized_queue(tmp_path)
    scheduler = SchedulerPlugin(queue)
    graph = _builder_graph()

    claimed = scheduler.claim("PX-EXEC-EWO-003", graph=graph)

    assert claimed.state == ExecutionState.CLAIMED
    assert len([e for e in bus.replay() if e.type == "JobClaimed"]) == 1
