from __future__ import annotations

from pathlib import Path

import pytest

from builder_engine.graph import BuilderGraph, Packet
from builder_engine.observe import GitObservation, ObservedSnapshot
from builder_engine.planner import PlanError, build_plan, critical_path, plan_ready
from builder_engine.policy import PolicyDecision
from builder_engine.state_io import save_raw_state


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _allow_policy() -> PolicyDecision:
    return PolicyDecision(outcome="allow", violations=(), warnings=())


def test_ready_parity_with_compute_ready():
    graph = BuilderGraph.load(_repo_root() / "plans" / "builder" / "STATE.example.yaml")
    snap = ObservedSnapshot(
        observed_at="t",
        state_path=str(graph.path),
        epic=graph.epic,
        chain=graph.chain,
        epic_status=graph.status,
        wave=graph.wave,
        packet_count=len(graph.packets),
        ready_count=3,
        in_flight_count=0,
        done_count=0,
        blocked_count=0,
        decisions_count=1,
        file_locks=(),
        blockers=(),
        packets=(),
        git=GitObservation(is_repo=False),
        validation_ok=True,
        validation_errors=(),
        validation_warnings=(),
        staleness_reasons=(),
    )
    plan = build_plan(snap, _allow_policy())
    assert set(plan.ready_packets) == {p.id for p in plan_ready(graph)}


def test_critical_path_chain():
    graph = BuilderGraph(
        path=Path("STATE.yaml"),
        epic="test",
        chain=None,
        status="active",
        wave=1,
        packets={
            "A": Packet("A", 1, "explorer", "done", (), ("docs/",)),
            "B": Packet("B", 1, "implementer", "ready", ("A",), ("backend/",), checks=("true",)),
            "C": Packet("C", 2, "integrator", "ready", ("B",), ("builder_engine/",)),
        },
    )
    path = critical_path(graph)
    assert path == ("A", "B", "C")


def test_blockers_copied_from_snapshot():
    graph = BuilderGraph.load(_repo_root() / "plans" / "builder" / "STATE.example.yaml")
    snap = ObservedSnapshot(
        observed_at="t",
        state_path=str(graph.path),
        epic=graph.epic,
        chain=graph.chain,
        epic_status="active",
        wave=graph.wave,
        packet_count=1,
        ready_count=0,
        in_flight_count=0,
        done_count=0,
        blocked_count=0,
        decisions_count=1,
        file_locks=(),
        blockers=(("P1", "blocked"),),
        packets=(),
        git=GitObservation(is_repo=False),
        validation_ok=True,
        validation_errors=(),
        validation_warnings=(),
        staleness_reasons=(),
    )
    plan = build_plan(snap, _allow_policy())
    assert plan.blockers == (("P1", "blocked"),)


def test_empty_plan_when_no_ready_and_wave_incomplete(tmp_path: Path):
    state_path = tmp_path / "STATE.yaml"
    save_raw_state(
        state_path,
        {
            "epic": "test",
            "status": "active",
            "wave": 1,
            "decisions": ["x"],
            "file_locks": {},
            "blockers": {},
            "packets": {
                "P1": {
                    "wave": 1,
                    "agent_type": "explorer",
                    "status": "in_progress",
                    "depends_on": [],
                    "owned_files": ["docs/"],
                    "checks": [],
                }
            },
        },
    )
    snap = ObservedSnapshot(
        observed_at="t",
        state_path=str(state_path),
        epic="test",
        chain=None,
        epic_status="active",
        wave=1,
        packet_count=1,
        ready_count=0,
        in_flight_count=1,
        done_count=0,
        blocked_count=0,
        decisions_count=1,
        file_locks=(),
        blockers=(),
        packets=(),
        git=GitObservation(is_repo=False),
        validation_ok=True,
        validation_errors=(),
        validation_warnings=(),
        staleness_reasons=(),
    )
    plan = build_plan(snap, _allow_policy())
    assert plan.empty is True
