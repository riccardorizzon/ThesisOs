from __future__ import annotations

from pathlib import Path

import pytest

from builder_engine.checks import CheckResult
from builder_engine.cycle import EngineeringRuntimeCycle
from builder_engine.events import BuildEventBus
from builder_engine.graph import BuilderGraph
from builder_engine.runtime import EngineeringRuntime
from builder_engine.state_io import load_raw_state, save_raw_state


def _bootstrap_repo(tmp_path: Path) -> Path:
    state_path = tmp_path / "plans" / "builder" / "STATE.yaml"
    state_path.parent.mkdir(parents=True)
    save_raw_state(
        state_path,
        {
            "epic": "mb2-integration",
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
        },
    )
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "safety.md").write_text("safe", encoding="utf-8")
    (tmp_path / "LOOP.md").write_text("loop", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("agents", encoding="utf-8")
    (tmp_path / "plans" / "builder" / "policies.yaml").write_text("version: 1\n", encoding="utf-8")
    return state_path


def test_full_dry_cycle_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    state_path = _bootstrap_repo(tmp_path)
    bus = BuildEventBus(tmp_path)

    pre = EngineeringRuntimeCycle(tmp_path, state_path, bus=bus).run_preflight()
    assert pre.policy.outcome != "block"

    runtime = EngineeringRuntime(tmp_path, state_path, bus=bus)
    sched = runtime.schedule()
    assert sched.packet_ids == ["P1"]
    assert BuilderGraph.load(state_path).packets["P1"].status == "in_progress"

    raw = load_raw_state(state_path)
    raw["packets"]["P1"]["checks"] = ["true"]
    save_raw_state(state_path, raw)

    monkeypatch.setattr(
        "builder_engine.runtime.run_packet_checks",
        lambda checks, root: [CheckResult(command="true", exit_code=0, stdout="", stderr="")],
    )

    sync = runtime.sync()
    assert sync.completed == ["P1"]

    proposal = EngineeringRuntimeCycle(tmp_path, state_path, bus=bus).run_postflight(
        sync, cycle_id=pre.cycle_id
    )
    assert proposal is None

    types = {e.type for e in bus.tail(50)}
    assert {"TaskScheduled", "ValidationPassed", "StateObserved"} <= types


def test_schedule_emits_events(tmp_path: Path):
    state_path = _bootstrap_repo(tmp_path)
    bus = BuildEventBus(tmp_path)
    EngineeringRuntime(tmp_path, state_path, bus=bus).schedule()
    types = {e.type for e in bus.tail(10)}
    assert "TaskScheduled" in types
    assert "LockAcquired" in types
