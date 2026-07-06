"""PX-EXEC-EWO-008 — Integration Plugin acceptance tests."""

from __future__ import annotations

from pathlib import Path

from builder_engine.events import BuildEvent, BuildEventBus
from builder_engine.integration import (
    IntegrationPlugin,
    execute_integration_action,
    register_integration_plugin,
)
from builder_engine.plugin_registry import PluginRegistry
from builder_engine.rules import ActionDescriptor, RuleEngine

FIXTURES = Path(__file__).resolve().parent / "fixtures"
INTEGRATION_CHECKS = FIXTURES / "integration_checks.yaml"
PX2_RULES = Path(__file__).resolve().parents[1] / "fixtures" / "px2_parallel_rules.yaml"


def _plugin(
    tmp_path: Path,
    *,
    ci_status: str | None = "passed",
    checks_fixture: Path | None = INTEGRATION_CHECKS,
) -> IntegrationPlugin:
    bus = BuildEventBus(tmp_path)
    return IntegrationPlugin(
        program_id="px2-parallel",
        bus=bus,
        cycle_id="integration-test",
        ci_status=ci_status,
        checks_fixture=checks_fixture,
    )


def test_integration_plugin_registers(tmp_path):
    registry = PluginRegistry()
    plugin = _plugin(tmp_path)
    register_integration_plugin(registry, plugin)

    descriptor = ActionDescriptor(
        plugin="integration",
        params={},
        rule_id="post-merge-integration",
        matched_event_id="MergeCompleted@test",
    )
    resolved = registry.resolve(descriptor)
    assert resolved is plugin
    assert registry.is_registered("integration")


def test_integration_start_on_merge_completed(tmp_path):
    plugin = _plugin(tmp_path)

    result = plugin.start(
        "wave-a-integration",
        merge_context={"merge_id": "merge-abc", "ewo_id": "PX2-EWO-003"},
    )

    assert result["outcome"] == "started"
    events = plugin.bus.replay()
    started = [e for e in events if e.type == "IntegrationStarted"]
    assert len(started) == 1
    assert started[0].payload["integration_id"] == "wave-a-integration"
    assert started[0].payload["merge_id"] == "merge-abc"


def test_integration_blocked_on_ci_fail(tmp_path):
    plugin = _plugin(tmp_path, ci_status="failed")

    result = plugin.start("wave-a-integration")

    assert result["outcome"] == "blocked"
    events = plugin.bus.replay()
    assert not any(e.type == "IntegrationStarted" for e in events)


def test_integration_passed_event(tmp_path):
    plugin = _plugin(tmp_path)
    plugin.start("wave-a-integration", merge_context={"merge_id": "merge-1"})

    check_result = plugin.run_checks()

    assert check_result["outcome"] == "passed"
    events = plugin.bus.replay()
    passed = [e for e in events if e.type == "IntegrationPassed"]
    assert len(passed) == 1
    assert passed[0].payload["integration_id"] == "wave-a-integration"


def test_integration_failed_event(tmp_path):
    plugin = _plugin(tmp_path)
    plugin.start("wave-c-integration", merge_context={"merge_id": "merge-2"})

    check_result = plugin.run_checks()

    assert check_result["outcome"] == "failed"
    events = plugin.bus.replay()
    failed = [e for e in events if e.type == "IntegrationFailed"]
    assert len(failed) == 1
    assert "coverage-gate" in failed[0].payload["reason"]


def test_rule_action_triggers_integration(tmp_path):
    plugin = _plugin(tmp_path)
    registry = PluginRegistry()
    register_integration_plugin(registry, plugin)
    engine = RuleEngine.from_pack_paths(
        [PX2_RULES],
        checkpoint={"ci_status": "passed"},
    )

    event = BuildEvent(
        type="MergeCompleted",
        timestamp="2026-07-06T00:00:00+00:00",
        payload={
            "merge_id": "merge-rule-test",
            "ewo_id": "PX2-EWO-003",
            "program_id": "px2-parallel",
            "ci_status": "passed",
        },
        program_id="px2-parallel",
    )
    descriptor = engine.evaluate(event)
    assert isinstance(descriptor, ActionDescriptor)
    assert descriptor.rule_id == "post-merge-integration"

    result = execute_integration_action(registry, descriptor, event_payload=event.payload)

    assert result["outcome"] == "passed"
    events = plugin.bus.replay()
    assert any(e.type == "IntegrationStarted" for e in events)
    assert any(e.type == "IntegrationPassed" for e in events)


def test_integration_report(tmp_path):
    plugin = _plugin(tmp_path)

    empty = plugin.report()
    assert empty["last_outcome"] == "none"

    plugin.start("wave-a-integration")
    plugin.run_checks()
    report = plugin.report()

    assert report["last_outcome"] == "passed"
    assert report["checks_run"] == 2


def test_fixture_ci_fail_blocks_via_integration_id(tmp_path):
    """wave-b-integration fixture has ci_status: failed — no IntegrationStarted."""
    plugin = _plugin(tmp_path, ci_status=None)

    result = plugin.start("wave-b-integration")

    assert result["outcome"] == "blocked"
    events = plugin.bus.replay()
    assert not any(e.type == "IntegrationStarted" for e in events)
