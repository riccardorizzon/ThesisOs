from __future__ import annotations

import ast
import logging
from pathlib import Path

import pytest

from builder_engine.events import BuildEvent, BuildEventBus, event_now
from builder_engine.rules import (
    ActionDescriptor,
    GovernanceGuardError,
    NoMatch,
    RuleEngine,
    RulePackError,
    load_rule_pack,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
PX2_PACK = FIXTURES / "px2_parallel_rules.yaml"
INVALID_GOVERNANCE = FIXTURES / "rule_pack_invalid_governance.yaml"
RULES_SOURCE = Path(__file__).resolve().parents[1] / "rules.py"


def _px2_engine(**checkpoint) -> RuleEngine:
    return RuleEngine.from_pack_paths([PX2_PACK], checkpoint=checkpoint)


def test_rule_pack_loads_schema_v1():
    pack = load_rule_pack(PX2_PACK)
    assert pack.schema_version == 1
    assert pack.program_id == "px2-parallel"
    assert len(pack.rules) == 4
    assert {r.id for r in pack.rules} == {
        "post-ewo-merge",
        "post-merge-integration",
        "post-integration-qwo",
        "qwo-escalate-supervisor",
    }


def test_rule_pack_invalid_schema_version(tmp_path: Path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "schema_version: 99\nprogram_id: x\nrules:\n  - id: r\n    priority: 1\n"
        "    on: EwoCompleted\n    action:\n      plugin: merge\n",
        encoding="utf-8",
    )
    with pytest.raises(RulePackError, match="unsupported schema_version"):
        load_rule_pack(bad)


def test_rule_priority_ordering():
    engine = _px2_engine()
    rules = engine.rules_for_program("px2-parallel")
    assert [r.id for r in rules] == [
        "post-ewo-merge",
        "post-merge-integration",
        "post-integration-qwo",
        "qwo-escalate-supervisor",
    ]
    assert [r.priority for r in rules] == [10, 20, 30, 40]


def test_deterministic_match():
    engine = _px2_engine(all_dependencies_satisfied=True)
    event = event_now(
        "EwoCompleted",
        {"ewo_id": "PX2-EWO-003"},
        program_id="px2-parallel",
        cycle_id="cycle-1",
    )
    event = BuildEvent(
        type=event.type,
        timestamp="2026-07-06T00:00:00+00:00",
        payload=event.payload,
        program_id=event.program_id,
        cycle_id=event.cycle_id,
    )
    first = engine.evaluate(event)
    second = engine.evaluate(event)
    assert isinstance(first, ActionDescriptor)
    assert first == second
    assert first.rule_id == "post-ewo-merge"
    assert first.plugin == "merge"


def test_no_match_logged(caplog: pytest.LogCaptureFixture):
    engine = _px2_engine()
    event = BuildEvent(
        type="EwoCompleted",
        timestamp="2026-07-06T00:00:00+00:00",
        payload={"all_dependencies_satisfied": False},
        program_id="px2-parallel",
    )
    result = engine.evaluate(event)
    assert isinstance(result, NoMatch)

    handler = engine.as_subscriber()
    with caplog.at_level(logging.DEBUG, logger="builder_engine.rules"):
        handler(event)
    assert "no rule match" in caplog.text


def test_governance_keys_rejected():
    with pytest.raises(GovernanceGuardError, match="forbidden governance guard"):
        load_rule_pack(INVALID_GOVERNANCE)


def test_px2_golden_post_ewo_merge():
    engine = _px2_engine(all_dependencies_satisfied=True)
    event = BuildEvent(
        type="EwoCompleted",
        timestamp="2026-07-06T00:00:00+00:00",
        payload={"ewo_id": "PX2-EWO-003"},
        program_id="px2-parallel",
    )
    result = engine.evaluate(event)
    assert isinstance(result, ActionDescriptor)
    assert result.rule_id == "post-ewo-merge"
    assert result.plugin == "merge"


def test_px2_golden_post_merge_integration():
    engine = _px2_engine(ci_status="passed")
    event = BuildEvent(
        type="MergeCompleted",
        timestamp="2026-07-06T00:00:00+00:00",
        payload={"merge_id": "m1"},
        program_id="px2-parallel",
    )
    result = engine.evaluate(event)
    assert isinstance(result, ActionDescriptor)
    assert result.rule_id == "post-merge-integration"
    assert result.plugin == "integration"


def test_px2_golden_post_integration_qwo():
    engine = _px2_engine(coverage_gate="passed")
    event = BuildEvent(
        type="IntegrationPassed",
        timestamp="2026-07-06T00:00:00+00:00",
        payload={"integration_id": "i1"},
        program_id="px2-parallel",
    )
    result = engine.evaluate(event)
    assert isinstance(result, ActionDescriptor)
    assert result.rule_id == "post-integration-qwo"
    assert result.plugin == "qualification"


def test_px2_golden_qwo_escalate_supervisor():
    engine = _px2_engine()
    event = BuildEvent(
        type="QwoPassed",
        timestamp="2026-07-06T00:00:00+00:00",
        payload={"qwo_id": "q1"},
        program_id="px2-parallel",
    )
    result = engine.evaluate(event)
    assert isinstance(result, ActionDescriptor)
    assert result.rule_id == "qwo-escalate-supervisor"
    assert result.plugin == "notification"
    assert result.params.get("target") == "Supervisor"


def test_subscriber_on_publish(tmp_path: Path):
    engine = _px2_engine(all_dependencies_satisfied=True)
    bus = BuildEventBus(tmp_path)
    seen: list[ActionDescriptor | NoMatch] = []

    def capture_handler(event):
        seen.append(engine.evaluate(event, {"all_dependencies_satisfied": True}))

    bus.subscribe(capture_handler)

    event = BuildEvent(
        type="EwoCompleted",
        timestamp="2026-07-06T00:00:00+00:00",
        payload={"ewo_id": "PX2-EWO-003"},
        program_id="px2-parallel",
    )
    bus.publish(event)

    assert len(seen) == 1
    assert isinstance(seen[0], ActionDescriptor)
    assert seen[0].rule_id == "post-ewo-merge"


def test_register_on_bus(tmp_path: Path, caplog: pytest.LogCaptureFixture):
    engine = _px2_engine()
    bus = BuildEventBus(tmp_path)
    engine.register(bus)

    no_match_event = BuildEvent(
        type="EwoCompleted",
        timestamp="2026-07-06T00:00:00+00:00",
        payload={},
        program_id="px2-parallel",
    )
    with caplog.at_level(logging.DEBUG, logger="builder_engine.rules"):
        bus.publish(no_match_event)
    assert "no rule match" in caplog.text


def test_policy_engine_not_used():
    source = RULES_SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert "policy" not in alias.name
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            assert "policy" not in module


def test_wildcard_pack_fallback(tmp_path: Path):
    specific = tmp_path / "specific_rules.yaml"
    specific.write_text(
        "schema_version: 1\nprogram_id: px2-parallel\nrules:\n"
        "  - id: specific-rule\n    priority: 1\n    on: JobReady\n"
        "    action:\n      plugin: scheduler\n      params: {}\n",
        encoding="utf-8",
    )
    wildcard = tmp_path / "wildcard_rules.yaml"
    wildcard.write_text(
        "schema_version: 1\nprogram_id: '*'\nrules:\n"
        "  - id: default-rule\n    priority: 99\n    on: JobReady\n"
        "    action:\n      plugin: noop\n      params: {}\n",
        encoding="utf-8",
    )
    engine = RuleEngine.from_fixtures_dir(tmp_path, "px2-parallel")
    rules = engine.rules_for_program("px2-parallel")
    assert len(rules) == 2
    assert rules[0].id == "specific-rule"
    assert rules[1].id == "default-rule"

    event = BuildEvent(
        type="JobReady",
        timestamp="2026-07-06T00:00:00+00:00",
        payload={},
        program_id="px2-parallel",
    )
    result = engine.evaluate(event)
    assert isinstance(result, ActionDescriptor)
    assert result.rule_id == "specific-rule"
