"""MB2-Q6 — Recovery qualification tests (normative test IDs).

SoR §13.2 MB2-Q6: FAILED → READY audit; checkpoint replay; MB2-Q-016…018.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from builder_engine.dependency import DependencyEngine
from builder_engine.events import BuildEvent, BuildEventBus
from builder_engine.graph import BuilderGraph, Packet
from builder_engine.job_queue import Job, JobQueue
from builder_engine.program_graph import load_program_graph
from builder_engine.recovery import (
    checkpoint_queue,
    restore_queue_from_checkpoint,
    restore_queue_from_replay,
    retry_failed_job,
)
from builder_engine.rules import ActionDescriptor, RuleEngine, load_rule_pack
from builder_engine.state_machine import ExecutionState, TransitionError

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
PX2_PACK = FIXTURES / "px2_parallel_rules.yaml"


def _fixtures_dir() -> Path:
    return Path(__file__).resolve().parent / "fixtures"


def _minimal_program():
    return load_program_graph(_fixtures_dir() / "px_exec_program_minimal.yaml")


def _materialized_queue(tmp_path: Path) -> tuple[JobQueue, BuildEventBus]:
    program = _minimal_program()
    bus = BuildEventBus(tmp_path)
    engine = DependencyEngine(program)
    graph = engine.derive(publish=False)
    queue = JobQueue(bus=bus, cycle_id="mb2-q6")
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


def _fixed_event(event_type: str, payload: dict, *, program_id: str = "px2-parallel") -> BuildEvent:
    return BuildEvent(
        type=event_type,
        timestamp="2026-07-06T00:00:00+00:00",
        payload=payload,
        program_id=program_id,
        cycle_id="mb2-q6",
    )


def test_mb2_q_016_failed_to_ready_emits_audit(tmp_path):
    """§12: FAILED → DEBUGGING → READY with RecoveryTaskCreated audit (REQ-15)."""
    job = Job(
        job_id="PX-EXEC-EWO-003",
        program_id="px-exec-test",
        ewo_id="PX-EXEC-EWO-003",
        state=ExecutionState.FAILED,
    )
    bus = BuildEventBus(tmp_path)

    recovered = retry_failed_job(job, bus=bus, cycle_id="rec-cycle")
    assert recovered.state == ExecutionState.READY

    events = bus.replay()
    recovery_events = [e for e in events if e.type == "RecoveryTaskCreated"]
    assert len(recovery_events) == 1
    audit = recovery_events[0]
    assert audit.payload["ewo_id"] == "PX-EXEC-EWO-003"
    assert audit.payload["from_state"] == "failed"
    assert audit.payload["to_state"] == "ready"
    assert audit.payload["recovery_type"] == "retry_job"

    ready_events = [e for e in events if e.type == "JobReady"]
    assert len(ready_events) == 1

    with pytest.raises(TransitionError, match="retry requires FAILED"):
        retry_failed_job(recovered, bus=bus)


def test_mb2_q_017_checkpoint_replay_restores_queue(tmp_path):
    """§12: checkpoint + event replay restores queue state (REQ-15)."""
    queue, bus = _materialized_queue(tmp_path)
    graph = _builder_graph()

    queue.claim("PX-EXEC-EWO-003", graph=graph)
    checkpoint = checkpoint_queue(queue)
    restored = restore_queue_from_checkpoint(checkpoint)

    assert restored.ready_queue() == queue.ready_queue()
    assert {
        job.job_id: job.state for job in restored.list_jobs()
    } == {
        job.job_id: job.state for job in queue.list_jobs()
    }

    replayed = restore_queue_from_replay(bus, cycle_id="mb2-q6")
    assert replayed.ready_queue() == queue.ready_queue()
    claimed = replayed.get("PX-EXEC-EWO-003")
    assert claimed is not None
    assert claimed.state == ExecutionState.CLAIMED


def test_mb2_q_018_px2_golden_path_replay():
    """§13.3: PX-2 parallel golden path rule sequence (REQ-16)."""
    engine = RuleEngine.from_pack_paths(
        [PX2_PACK],
        checkpoint={
            "all_dependencies_satisfied": True,
            "ci_status": "passed",
            "coverage_gate": "passed",
        },
    )
    sequence = [
        (
            _fixed_event("EwoCompleted", {"ewo_id": "PX2-EWO-003"}),
            "post-ewo-merge",
            "merge",
        ),
        (
            _fixed_event("MergeCompleted", {"merge_id": "m1"}),
            "post-merge-integration",
            "integration",
        ),
        (
            _fixed_event("IntegrationPassed", {"integration_id": "i1"}),
            "post-integration-qwo",
            "qualification",
        ),
        (
            _fixed_event("QwoPassed", {"qwo_id": "QWO-PX2-001"}),
            "qwo-escalate-supervisor",
            "notification",
        ),
    ]
    for event, rule_id, plugin in sequence:
        result = engine.evaluate(event)
        assert isinstance(result, ActionDescriptor), f"expected match for {event.type}"
        assert result.rule_id == rule_id
        assert result.plugin == plugin

    pack = load_rule_pack(PX2_PACK)
    assert len(pack.rules) == 4
