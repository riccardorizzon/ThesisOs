from __future__ import annotations

import json
from pathlib import Path

import pytest

from builder_engine.graph import BuilderGraph, Packet
from builder_engine.observe import ObservedSnapshot, StateObserver
from builder_engine.scheduler import compute_ready


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_observe_loads_state_example():
    observer = StateObserver(_repo_root())
    snap = observer.observe()
    assert isinstance(snap, ObservedSnapshot)
    assert snap.epic
    assert snap.packet_count >= 1
    assert snap.is_complete or snap.staleness_reasons


def test_observe_counts_match_graph():
    root = _repo_root()
    graph = BuilderGraph.load(root / "plans" / "builder" / "STATE.example.yaml")
    observer = StateObserver(root, state_path=graph.path)
    snap = observer.observe()

    assert snap.ready_count == len(compute_ready(graph))
    assert snap.in_flight_count == len(
        [p for p in graph.packets.values() if p.status == "in_progress"]
    )
    assert snap.packet_count == len(graph.packets)
    assert len(snap.file_locks) == len(graph.file_locks)
    assert len(snap.blockers) == len(graph.blockers)


def test_observe_git_fields_in_repo():
    snap = StateObserver(_repo_root()).observe()
    assert snap.git.is_repo is True
    assert snap.git.branch is not None


def test_observe_missing_state():
    snap = StateObserver(_repo_root(), state_path=Path("/nonexistent/STATE.yaml")).observe()
    assert not snap.is_complete
    assert any("not found" in r for r in snap.staleness_reasons)


def test_observe_unreadable_state(tmp_path: Path):
    bad = tmp_path / "STATE.yaml"
    bad.write_text("- orphan list item\n", encoding="utf-8")
    snap = StateObserver(tmp_path, state_path=bad).observe()
    assert not snap.is_complete
    assert any("failed to parse" in r.lower() for r in snap.staleness_reasons)


def test_observe_blockers_mark_stale():
    graph_path = _repo_root() / "plans" / "builder" / "STATE.example.yaml"
    graph = BuilderGraph(
        path=graph_path,
        epic="test",
        chain=None,
        status="active",
        wave=1,
        blockers={"P1": "needs human"},
        packets={
            "P1": Packet(
                id="P1",
                wave=1,
                agent_type="explorer",
                status="ready",
                depends_on=(),
                owned_files=("backend/",),
            ),
        },
    )
    from builder_engine.observe import _build_snapshot
    from builder_engine.observe import GitObservation

    snap = _build_snapshot(
        graph,
        git=GitObservation(is_repo=False),
        validation_ok=True,
        validation_errors=(),
        validation_warnings=(),
    )
    assert not snap.is_complete
    assert any("blocker" in r for r in snap.staleness_reasons)


def test_snapshot_is_json_serializable():
    snap = StateObserver(_repo_root()).observe()
    payload = {
        "epic": snap.epic,
        "wave": snap.wave,
        "ready_count": snap.ready_count,
        "is_complete": snap.is_complete,
        "staleness_reasons": list(snap.staleness_reasons),
    }
    json.dumps(payload)
