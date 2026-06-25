from __future__ import annotations

from pathlib import Path

import pytest

from builder_engine.checks import CheckResult
from builder_engine.graph import BuilderGraph
from builder_engine.runtime import WorkflowRuntime, WorkflowRuntimeError
from builder_engine.state_io import save_raw_state


def _write_state(path: Path, *, wave: int = 1, packets: dict | None = None) -> None:
    save_raw_state(
        path,
        {
            "epic": "test-runtime",
            "chain": None,
            "status": "active",
            "wave": wave,
            "decisions": ["test"],
            "file_locks": {},
            "blockers": {},
            "packets": packets
            or {
                "P1": {
                    "wave": 1,
                    "agent_type": "explorer",
                    "status": "ready",
                    "depends_on": [],
                    "owned_files": ["docs/"],
                    "checks": [],
                }
            },
        },
    )


def test_schedule_claims_packet_and_writes_manifest(tmp_path: Path):
    state_path = tmp_path / "STATE.yaml"
    _write_state(state_path)
    runtime = WorkflowRuntime(tmp_path, state_path)

    result = runtime.schedule()

    assert result.packet_ids == ["P1"]
    assert result.manifest_path.is_file()
    graph = BuilderGraph.load(state_path)
    assert graph.packets["P1"].status == "in_progress"
    assert graph.file_locks == {"docs/": "P1"}


def test_schedule_refuses_implementer_without_checks(tmp_path: Path):
    state_path = tmp_path / "STATE.yaml"
    _write_state(
        state_path,
        packets={
            "P1": {
                "wave": 1,
                "agent_type": "implementer",
                "status": "ready",
                "depends_on": [],
                "owned_files": ["backend/"],
                "checks": [],
            }
        },
    )
    runtime = WorkflowRuntime(tmp_path, state_path)

    with pytest.raises(WorkflowRuntimeError, match="requires checks"):
        runtime.schedule()


def test_sync_marks_done_and_advances_wave(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    state_path = tmp_path / "STATE.yaml"
    _write_state(
        state_path,
        wave=1,
        packets={
            "P1": {
                "wave": 1,
                "agent_type": "explorer",
                "status": "in_progress",
                "depends_on": [],
                "owned_files": ["docs/"],
                "checks": ["true"],
            },
            "P2": {
                "wave": 2,
                "agent_type": "explorer",
                "status": "ready",
                "depends_on": ["P1"],
                "owned_files": ["builder_engine/"],
                "checks": [],
            },
        },
    )
    runtime = WorkflowRuntime(tmp_path, state_path)

    monkeypatch.setattr(
        "builder_engine.runtime.run_packet_checks",
        lambda checks, root: [CheckResult(command="true", exit_code=0, stdout="", stderr="")],
    )

    result = runtime.sync()

    assert result.completed == ["P1"]
    assert result.advanced_to_wave == 2
    graph = BuilderGraph.load(state_path)
    assert graph.packets["P1"].status == "done"
    assert graph.wave == 2
    assert graph.file_locks == {}


def test_sync_blocks_on_failed_checks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    state_path = tmp_path / "STATE.yaml"
    _write_state(
        state_path,
        packets={
            "P1": {
                "wave": 1,
                "agent_type": "implementer",
                "status": "in_progress",
                "depends_on": [],
                "owned_files": ["backend/"],
                "checks": ["false"],
            }
        },
    )
    runtime = WorkflowRuntime(tmp_path, state_path)

    monkeypatch.setattr(
        "builder_engine.runtime.run_packet_checks",
        lambda checks, root: [CheckResult(command="false", exit_code=1, stdout="", stderr="fail")],
    )

    result = runtime.sync()

    assert result.failed == ["P1"]
    graph = BuilderGraph.load(state_path)
    assert graph.packets["P1"].status == "blocked"
