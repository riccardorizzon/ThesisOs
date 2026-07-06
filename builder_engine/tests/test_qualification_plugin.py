"""PX-EXEC-EWO-009 — Qualification Plugin acceptance tests."""

from __future__ import annotations

from pathlib import Path

from builder_engine.events import BuildEvent, BuildEventBus
from builder_engine.plugin_registry import PluginRegistry
from builder_engine.projection import ProjectionBuilder
from builder_engine.qualification import (
    QualificationPlugin,
    execute_qualification_action,
    register_qualification_plugin,
)
from builder_engine.rules import ActionDescriptor, RuleEngine

FIXTURES = Path(__file__).resolve().parent / "fixtures"
QWO_SPAWN_CONTEXT = FIXTURES / "qwo_spawn_context.yaml"
PX2_RULES = Path(__file__).resolve().parents[1] / "fixtures" / "px2_parallel_rules.yaml"


def _plugin(
    tmp_path: Path,
    *,
    coverage_gate: str | None = "passed",
    spawn_fixture: Path | None = QWO_SPAWN_CONTEXT,
) -> QualificationPlugin:
    bus = BuildEventBus(tmp_path)
    return QualificationPlugin(
        program_id="px2-parallel",
        bus=bus,
        cycle_id="qualification-test",
        coverage_gate=coverage_gate,
        spawn_fixture=spawn_fixture,
    )


def test_qualification_plugin_registers(tmp_path):
    registry = PluginRegistry()
    plugin = _plugin(tmp_path)
    register_qualification_plugin(registry, plugin)

    descriptor = ActionDescriptor(
        plugin="qualification",
        params={},
        rule_id="post-integration-qwo",
        matched_event_id="IntegrationPassed@test",
    )
    resolved = registry.resolve(descriptor)
    assert resolved is plugin
    assert registry.is_registered("qualification")


def test_qwo_spawn_on_integration_passed(tmp_path):
    plugin = _plugin(tmp_path)

    result = plugin.spawn(
        "QWO-default",
        integration_context={
            "integration_id": "wave-a-integration",
            "merge_id": "merge-abc",
            "ewo_id": "PX2-EWO-003",
        },
    )

    assert result["outcome"] == "spawned"
    assert result["qwo_id"] == "QWO-PX2-001"
    events = plugin.bus.replay()
    spawned = [e for e in events if e.type == "QwoSpawned"]
    assert len(spawned) == 1
    assert spawned[0].payload["qwo_id"] == "QWO-PX2-001"
    assert spawned[0].payload["merge_id"] == "merge-abc"


def test_qwo_blocked_on_coverage_fail(tmp_path):
    plugin = _plugin(tmp_path, coverage_gate="failed")

    result = plugin.spawn("QWO-default", integration_context={"integration_id": "wave-a-integration"})

    assert result["outcome"] == "blocked"
    events = plugin.bus.replay()
    assert not any(e.type == "QwoSpawned" for e in events)


def test_qwo_blocked_on_fixture_coverage_fail(tmp_path):
    plugin = _plugin(tmp_path, coverage_gate=None)

    result = plugin.spawn("QWO-default", integration_context={"integration_id": "wave-b-integration"})

    assert result["outcome"] == "blocked"
    events = plugin.bus.replay()
    assert not any(e.type == "QwoSpawned" for e in events)


def test_qwo_failed_escalates(tmp_path):
    plugin = _plugin(tmp_path)

    result = plugin.spawn("QWO-default", integration_context={"integration_id": "wave-c-integration"})

    assert result["outcome"] == "failed"
    events = plugin.bus.replay()
    failed = [e for e in events if e.type == "QwoFailed"]
    escalated = [e for e in events if e.type == "RuntimeEscalated"]
    assert len(failed) == 1
    assert len(escalated) == 1
    assert escalated[0].payload["supervisor_action"] == "WAIT"

    builder = ProjectionBuilder()
    for event in events:
        builder.apply(event)
    assert builder.document.supervisor["state"] == "WAIT"


def test_rule_action_triggers_qualification(tmp_path):
    plugin = _plugin(tmp_path)
    registry = PluginRegistry()
    register_qualification_plugin(registry, plugin)
    engine = RuleEngine.from_pack_paths(
        [PX2_RULES],
        checkpoint={"coverage_gate": "passed"},
    )

    event = BuildEvent(
        type="IntegrationPassed",
        timestamp="2026-07-06T00:00:00+00:00",
        payload={
            "integration_id": "wave-a-integration",
            "merge_id": "merge-rule-test",
            "ewo_id": "PX2-EWO-003",
            "program_id": "px2-parallel",
            "coverage_gate": "passed",
        },
        program_id="px2-parallel",
    )
    descriptor = engine.evaluate(event)
    assert isinstance(descriptor, ActionDescriptor)
    assert descriptor.rule_id == "post-integration-qwo"

    result = execute_qualification_action(registry, descriptor, event_payload=event.payload)

    assert result["outcome"] == "collected"
    events = plugin.bus.replay()
    assert any(e.type == "QwoSpawned" for e in events)


def test_collect_evidence_structure(tmp_path):
    plugin = _plugin(tmp_path)
    plugin.spawn("QWO-default", integration_context={"integration_id": "wave-a-integration"})

    evidence = plugin.collect_evidence()
    report = plugin.report()

    assert evidence["outcome"] == "collected"
    assert evidence["evidence_refs"]
    assert report["last_outcome"] == "collected"
    assert report["evidence_refs"] == evidence["evidence_refs"]


def test_qualification_report_empty(tmp_path):
    plugin = _plugin(tmp_path)

    report = plugin.report()

    assert report["last_outcome"] == "none"
    assert report["qwo_id"] is None
