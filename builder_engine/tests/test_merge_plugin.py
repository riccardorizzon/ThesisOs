"""PX-EXEC-EWO-007 — Merge Plugin acceptance tests."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from builder_engine.events import BuildEvent, BuildEventBus, event_now
from builder_engine.merge import (
    MergeContext,
    MergePlugin,
    execute_merge_action,
    merge_eligibility,
    register_merge_plugin,
)
from builder_engine.plugin_registry import PluginRegistry
from builder_engine.program_graph import load_program_graph
from builder_engine.rules import ActionDescriptor, RuleEngine

FIXTURES = Path(__file__).resolve().parent / "fixtures"
MERGE_ORDER_GRAPH = FIXTURES / "merge_order_graph.yaml"
PX2_RULES = Path(__file__).resolve().parents[1] / "fixtures" / "px2_parallel_rules.yaml"
MERGE_SOURCE = Path(__file__).resolve().parents[1] / "merge.py"


def _program():
    return load_program_graph(MERGE_ORDER_GRAPH)


def _plugin(tmp_path: Path, *, completed: set[str] | None = None) -> MergePlugin:
    bus = BuildEventBus(tmp_path)
    return MergePlugin(_program(), bus=bus, cycle_id="merge-test", completed_merges=completed)


def test_merge_plugin_registers(tmp_path):
    registry = PluginRegistry()
    plugin = _plugin(tmp_path)
    register_merge_plugin(registry, plugin)

    descriptor = ActionDescriptor(
        plugin="merge",
        params={},
        rule_id="post-ewo-merge",
        matched_event_id="EwoCompleted@test",
    )
    resolved = registry.resolve(descriptor)
    assert resolved is plugin
    assert registry.is_registered("merge")


def test_merge_order_enforced(tmp_path):
    plugin = _plugin(tmp_path)

    first = plugin.eligible("PX-MERGE-002")
    assert first.outcome == "eligible"

    second = plugin.eligible("PX-MERGE-003")
    assert second.outcome == "rejected"
    assert "merge_order violation" in second.reason


def test_merge_order_satisfied_after_prior_complete(tmp_path):
    plugin = _plugin(tmp_path, completed={"PX-MERGE-002"})

    result = plugin.eligible("PX-MERGE-003")
    assert result.outcome == "eligible"


def test_merge_execute_emits_completed(tmp_path):
    plugin = _plugin(tmp_path)
    ctx = MergeContext(
        job_id="PX-MERGE-002",
        program_id="merge-order-test",
        ewo_id="PX-MERGE-002",
        packet_ids=("PX-MERGE-002",),
        merge_order_index=0,
    )

    result = plugin.execute(ctx)

    assert result.outcome == "completed"
    assert result.merge_id is not None
    events = plugin.bus.replay()
    completed = [e for e in events if e.type == "MergeCompleted"]
    assert len(completed) == 1
    assert completed[0].payload["ewo_id"] == "PX-MERGE-002"
    assert completed[0].payload["merge_id"] == result.merge_id


def test_merge_execute_emits_failed(tmp_path):
    plugin = _plugin(tmp_path)
    ctx = MergeContext(
        job_id="PX-MERGE-003",
        program_id="merge-order-test",
        ewo_id="PX-MERGE-003",
        packet_ids=("PX-MERGE-003",),
        merge_order_index=1,
    )

    result = plugin.execute(ctx)

    assert result.outcome == "rejected"
    events = plugin.bus.replay()
    failed = [e for e in events if e.type == "MergeFailed"]
    assert len(failed) == 1
    assert failed[0].payload["ewo_id"] == "PX-MERGE-003"


def test_no_git_mutation():
    """Era I D8 — merge module must not invoke git subprocess."""
    source = MERGE_SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name != "subprocess"
        elif isinstance(node, ast.ImportFrom):
            assert (node.module or "") != "subprocess"
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in ("run", "Popen", "call"):
                if isinstance(func.value, ast.Name) and func.value.id == "subprocess":
                    pytest.fail("merge.py must not call subprocess")
            if isinstance(func, ast.Name) and func.id in ("git",):
                pytest.fail("merge.py must not invoke git directly")


def test_rule_action_triggers_merge(tmp_path):
    plugin = _plugin(tmp_path)
    registry = PluginRegistry()
    register_merge_plugin(registry, plugin)
    engine = RuleEngine.from_pack_paths(
        [PX2_RULES],
        checkpoint={"all_dependencies_satisfied": True},
    )

    event = BuildEvent(
        type="EwoCompleted",
        timestamp="2026-07-06T00:00:00+00:00",
        payload={"ewo_id": "PX2-EWO-003"},
        program_id="px2-parallel",
    )
    descriptor = engine.evaluate(event)
    assert isinstance(descriptor, ActionDescriptor)

    # Use merge-order-test program plugin with px2 event ewo_id overridden in payload
    plugin.program = _program()
    result = execute_merge_action(
        registry,
        descriptor,
        event_payload={"ewo_id": "PX-MERGE-002"},
    )

    assert result.outcome == "completed"
    events = plugin.bus.replay()
    assert any(e.type == "MergeCompleted" for e in events)


def test_merge_report(tmp_path):
    plugin = _plugin(tmp_path)

    empty = plugin.report()
    assert empty["last_outcome"] == "none"

    ctx = MergeContext(
        job_id="PX-MERGE-002",
        program_id="merge-order-test",
        ewo_id="PX-MERGE-002",
        packet_ids=("PX-MERGE-002",),
        merge_order_index=0,
    )
    plugin.execute(ctx)
    report = plugin.report()

    assert report["last_outcome"] == "completed"
    assert report["completed_count"] == 1
    assert report["merge_id"] is not None


def test_era_i_merge_eligibility_unchanged():
    passed = merge_eligibility(validation_passed=True, packet_ids=("P1",))
    assert passed.outcome == "deferred"

    failed = merge_eligibility(validation_passed=False)
    assert failed.outcome == "rejected"


def test_manifest_written_for_external_integrator(tmp_path):
    plugin = _plugin(tmp_path)
    ctx = MergeContext(
        job_id="PX-MERGE-002",
        program_id="merge-order-test",
        ewo_id="PX-MERGE-002",
        packet_ids=("PX-MERGE-002",),
        merge_order_index=0,
    )
    plugin.execute(ctx)

    manifest_path = tmp_path / ".builder-engine" / "last-merge-manifest.json"
    assert manifest_path.is_file()
    assert "external" in manifest_path.read_text(encoding="utf-8")
