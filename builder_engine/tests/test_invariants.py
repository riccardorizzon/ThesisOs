from __future__ import annotations

from pathlib import Path

import pytest

from builder_engine.invariants import InvariantViolation, check_invariants, check_raw_state
from builder_engine.state_io import save_raw_state


def _valid_state() -> dict:
    return {
        "epic": "test",
        "chain": None,
        "status": "active",
        "wave": 1,
        "decisions": ["test"],
        "file_locks": {},
        "blockers": {},
        "packets": {
            "P1": {
                "wave": 1,
                "agent_type": "explorer",
                "status": "ready",
                "depends_on": [],
                "owned_files": ["docs/"],
                "checks": [],
            }
        },
    }


def test_check_invariants_valid_graph():
    from builder_engine.invariants import graph_from_state_dict

    check_invariants(graph_from_state_dict(_valid_state(), Path("STATE.yaml")))


def test_inv_b6_wave_mismatch_raises():
    data = _valid_state()
    data["wave"] = 2
    data["packets"]["P1"]["status"] = "in_progress"
    data["packets"]["P1"]["wave"] = 1
    with pytest.raises(InvariantViolation, match="in_progress"):
        check_raw_state(data, Path("STATE.yaml"))


def test_save_raw_state_runs_invariant_pass(tmp_path: Path):
    path = tmp_path / "STATE.yaml"
    save_raw_state(path, _valid_state())


def test_save_raw_state_rejects_invalid(tmp_path: Path):
    path = tmp_path / "STATE.yaml"
    data = _valid_state()
    data["packets"]["P1"]["depends_on"] = ["MISSING"]
    with pytest.raises(InvariantViolation):
        save_raw_state(path, data)
