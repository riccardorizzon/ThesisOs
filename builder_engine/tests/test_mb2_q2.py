"""MB2-Q2 — Rule Engine qualification tests (normative test IDs).

SoR §13.2 MB2-Q2: deterministic rule evaluation; golden PX-2 rules;
MB2-Q-004…006. No new implementation — evidence on EWO-002 artifacts.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from builder_engine.events import BuildEvent, BuildEventBus
from builder_engine.rules import (
    ActionDescriptor,
    GovernanceGuardError,
    NoMatch,
    RuleEngine,
    load_rule_pack,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
PX2_PACK = FIXTURES / "px2_parallel_rules.yaml"
INVALID_GOVERNANCE = FIXTURES / "rule_pack_invalid_governance.yaml"
RULES_SOURCE = Path(__file__).resolve().parents[1] / "rules.py"


def _px2_engine(**checkpoint) -> RuleEngine:
    return RuleEngine.from_pack_paths([PX2_PACK], checkpoint=checkpoint)


def _fixed_event(event_type: str, payload: dict, *, program_id: str = "px2-parallel") -> BuildEvent:
    return BuildEvent(
        type=event_type,
        timestamp="2026-07-06T00:00:00+00:00",
        payload=payload,
        program_id=program_id,
        cycle_id="mb2-q2",
    )


def test_mb2_q_004_same_event_state_same_action():
    """INV-R-13: deterministic evaluation (REQ-09)."""
    engine = _px2_engine(all_dependencies_satisfied=True)
    event = _fixed_event("EwoCompleted", {"ewo_id": "PX2-EWO-003"})
    first = engine.evaluate(event)
    second = engine.evaluate(event)
    third = engine.evaluate(event)
    assert isinstance(first, ActionDescriptor)
    assert first == second == third
    assert first.rule_id == "post-ewo-merge"
    assert first.plugin == "merge"

    no_match = _fixed_event("EwoCompleted", {"all_dependencies_satisfied": False})
    assert isinstance(engine.evaluate(no_match), NoMatch)
    assert engine.evaluate(no_match) == engine.evaluate(no_match)


def test_mb2_q_004_subscriber_redelivery_deterministic(tmp_path):
    """REQ-18 hook: handler replay yields same descriptor."""
    engine = _px2_engine(all_dependencies_satisfied=True)
    bus = BuildEventBus(tmp_path)
    results: list[ActionDescriptor | NoMatch] = []
    bus.subscribe(lambda ev: results.append(engine.evaluate(ev, {"all_dependencies_satisfied": True})))

    event = _fixed_event("EwoCompleted", {"ewo_id": "PX2-EWO-003"})
    bus.publish(event)
    bus.redeliver(event)

    assert len(results) == 2
    assert results[0] == results[1]
    assert isinstance(results[0], ActionDescriptor)


def test_mb2_q_005_governance_policy_not_in_rule_pack():
    """INV-R-07: forbidden governance guard keys rejected (REQ-06)."""
    with pytest.raises(GovernanceGuardError, match="forbidden governance guard"):
        load_rule_pack(INVALID_GOVERNANCE)

    source = RULES_SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert "policy" not in alias.name
        elif isinstance(node, ast.ImportFrom):
            assert "policy" not in (node.module or "")


def test_mb2_q_006_px2_golden_rules_replay():
    """SoR §7.3: full golden path rule sequence."""
    engine = _px2_engine(
        all_dependencies_satisfied=True,
        ci_status="passed",
        coverage_gate="passed",
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
    assert [r.priority for r in sorted(pack.rules, key=lambda r: r.priority)] == [10, 20, 30, 40]
