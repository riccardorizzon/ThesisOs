from __future__ import annotations

import json
from pathlib import Path

import pytest

from builder_engine.graph import BuilderGraph, Packet
from builder_engine.observe import GitObservation, ObservedSnapshot, StateObserver, _build_snapshot
from builder_engine.policy import PolicyEngine, PolicyViolation, default_policies_path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _snapshot(**overrides) -> ObservedSnapshot:
    base = {
        "observed_at": "2026-06-28T00:00:00+00:00",
        "state_path": "/tmp/STATE.yaml",
        "epic": "test-epic",
        "chain": None,
        "epic_status": "active",
        "wave": 1,
        "packet_count": 1,
        "ready_count": 1,
        "in_flight_count": 0,
        "done_count": 0,
        "blocked_count": 0,
        "decisions_count": 1,
        "file_locks": (),
        "blockers": (),
        "packets": (),
        "git": GitObservation(is_repo=False),
        "validation_ok": True,
        "validation_errors": (),
        "validation_warnings": (),
        "staleness_reasons": (),
    }
    base.update(overrides)
    return ObservedSnapshot(**base)


def test_invalid_graph_blocks():
    snap = _snapshot(
        validation_ok=False,
        validation_errors=("missing epic",),
        staleness_reasons=("graph validation failed", "missing epic"),
    )
    decision = PolicyEngine(_repo_root()).evaluate(snap)
    assert decision.outcome == "block"
    assert any(v.rule_id == "invariant.graph_invalid" for v in decision.violations)


def test_ready_implementer_without_checks_blocks():
    from builder_engine.observe import PacketSummary

    snap = _snapshot(
        packets=(
            PacketSummary(
                id="P1",
                wave=1,
                status="ready",
                agent_type="implementer",
                depends_on=(),
                checks=(),
            ),
        ),
    )
    decision = PolicyEngine(_repo_root()).evaluate(snap)
    assert decision.outcome == "block"
    assert any(v.rule_id == "packet.implementer_requires_checks" for v in decision.violations)


def test_warnings_only_allows():
    snap = _snapshot(
        validation_warnings=("no decisions listed — add frozen contracts",),
    )
    decision = PolicyEngine(_repo_root()).evaluate(snap)
    assert decision.outcome == "allow"
    assert decision.warnings


def test_yaml_missing_file_blocks(tmp_path: Path):
    policies = tmp_path / "policies.yaml"
    policies.write_text(
        "require_files:\n"
        "  missing-gate:\n"
        "    path: docs/does-not-exist-gate.md\n"
        "    message: gate doc missing\n"
        "    action: block\n",
        encoding="utf-8",
    )
    snap = _snapshot()
    decision = PolicyEngine(tmp_path, policies_path=policies).evaluate(snap)
    assert decision.outcome == "block"
    assert any(v.rule_id == "missing-gate" for v in decision.violations)


def test_yaml_escalate_allows_continue(tmp_path: Path):
    policies = tmp_path / "policies.yaml"
    policies.write_text(
        "rules:\n"
        "  dirty-git-hint:\n"
        "    action: escalate\n"
        "    message: git dirty — review before merge\n"
        "    when:\n"
        "      epic_prefix: test\n",
        encoding="utf-8",
    )
    snap = _snapshot(epic="test-epic")
    decision = PolicyEngine(tmp_path, policies_path=policies).evaluate(snap)
    assert decision.outcome == "escalate"
    assert decision.violations
    assert not any(v.action == "block" for v in decision.violations)


def test_repo_policies_yaml_loads():
    path = default_policies_path(_repo_root())
    assert path.is_file()
    snap = StateObserver(_repo_root()).observe()
    decision = PolicyEngine(_repo_root(), path).evaluate(snap)
    assert decision.outcome in ("allow", "escalate", "block")


def test_closed_epic_escalates_when_active_epic_closed():
    snap = _snapshot(epic_status="closed")
    decision = PolicyEngine(_repo_root()).evaluate(snap)
    assert decision.outcome == "escalate"
    assert any(v.rule_id == "closed-epic-schedule-hint" for v in decision.violations)


def test_open_blockers_block():
    snap = _snapshot(blockers=(("P1", "needs human"),))
    decision = PolicyEngine(_repo_root()).evaluate(snap)
    assert decision.outcome == "block"
    assert any(v.rule_id == "workflow.open_blockers" for v in decision.violations)


def test_policy_decision_json_serializable():
    snap = _snapshot()
    decision = PolicyEngine(_repo_root()).evaluate(snap)
    payload = {
        "outcome": decision.outcome,
        "violations": [{"rule_id": v.rule_id, "message": v.message} for v in decision.violations],
    }
    json.dumps(payload)
