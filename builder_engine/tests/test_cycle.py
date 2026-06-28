from __future__ import annotations

from pathlib import Path

import pytest

from builder_engine.cycle import EngineeringRuntimeCycle
from builder_engine.events import BuildEventBus
from builder_engine.merge import merge_eligibility
from builder_engine.replan import minimal_replan
from builder_engine.runtime import SyncResult


def test_merge_check_always_deferred_when_passed():
    result = merge_eligibility(validation_passed=True, packet_ids=("P1",))
    assert result.outcome == "deferred"


def test_merge_rejected_on_failed_validation():
    result = merge_eligibility(validation_passed=False)
    assert result.outcome == "rejected"


def test_replan_proposal_on_validation_failed():
    sync = SyncResult(completed=[], failed=["P1"])
    proposal = minimal_replan(sync)
    assert proposal is not None
    assert "P1" in proposal.failed_packets
    assert proposal.recovery_packet_snippet


def test_replan_does_not_write_state(tmp_path: Path):
    state = tmp_path / "plans" / "builder" / "STATE.yaml"
    state.parent.mkdir(parents=True)
    state.write_text("epic: test\nwave: 1\npackets: {}\n", encoding="utf-8")
    before = state.read_text()
    minimal_replan(SyncResult(failed=["P1"]), bus=BuildEventBus(tmp_path))
    assert state.read_text() == before


def test_cycle_preflight_dry_run(tmp_path: Path):
    state = tmp_path / "plans" / "builder" / "STATE.yaml"
    state.parent.mkdir(parents=True)
    state.write_text(
        "epic: cycle-test\nstatus: active\nwave: 1\ndecisions: [x]\nfile_locks: {}\n"
        "blockers: {}\npackets:\n  P1:\n    wave: 1\n    agent_type: explorer\n"
        "    status: done\n    depends_on: []\n    owned_files: [docs/]\n    checks: []\n",
        encoding="utf-8",
    )
    (tmp_path / "docs").mkdir(parents=True)
    (tmp_path / "docs" / "safety.md").write_text("s", encoding="utf-8")
    (tmp_path / "LOOP.md").write_text("l", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("a", encoding="utf-8")

    policies = tmp_path / "plans" / "builder" / "policies.yaml"
    policies.write_text("version: 1\n", encoding="utf-8")

    result = EngineeringRuntimeCycle(tmp_path, state).run_preflight()
    assert result.policy.outcome in ("allow", "escalate")
    events = BuildEventBus(tmp_path).tail(20)
    types = {e.type for e in events}
    assert "CycleStarted" in types
    assert "StateObserved" in types
