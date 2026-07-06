"""§13.3 golden path replay audit — live plugin chain + manual trail equivalence."""

from __future__ import annotations

from pathlib import Path

from builder_engine.events import BuildEvent
from builder_engine.golden_path import (
    GOLDEN_PATH_STAGES,
    MANUAL_AUDIT_TRAIL,
    expected_lifecycle_event_types,
    replay_px2_golden_path,
    replay_stage,
    wave_merge_order,
    build_golden_path_runtime,
)
from builder_engine.program_graph import load_program_graph
from builder_engine.rules import ActionDescriptor, RuleEngine

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
PX2_PROGRAM = FIXTURES / "px2_golden_path_program.yaml"
PX2_RULES = FIXTURES / "px2_parallel_rules.yaml"


def test_golden_path_program_matches_px2_parallel_merge_orders():
    """Program fixture merge_order aligns with px2-parallel.yaml."""
    program = load_program_graph(PX2_PROGRAM)
    assert wave_merge_order(program, "wave_a") == ("PX2-EWO-001", "PX2-EWO-002", "PX2-EWO-005")
    assert wave_merge_order(program, "wave_b") == ("PX2-EWO-003", "PX2-EWO-004", "PX2-EWO-006")
    assert wave_merge_order(program, "wave_c") == ("PX2-EWO-007",)
    assert wave_merge_order(program, "wave_d") == ("PX2-EWO-008",)


def test_golden_path_full_replay_live_plugins(tmp_path):
    """§13.3: audited replay through merge → integration → qualification plugins."""
    result = replay_px2_golden_path(tmp_path)

    assert result.passed
    assert len(result.stages) == 4
    assert all(stage.outcome == "pass" for stage in result.stages)
    assert result.stages[-1].qwo_id == "QWO-PX2-001"

    for expected in expected_lifecycle_event_types():
        assert expected in result.event_types, f"missing {expected} in replay log"

    merge_count = result.event_types.count("MergeCompleted")
    integration_pass_count = result.event_types.count("IntegrationPassed")
    assert merge_count == 4
    assert integration_pass_count == 4
    assert result.event_types.count("QwoSpawned") == 1


def test_golden_path_manual_audit_trail_refs_exist():
    """Manual PX-2 execution audit artifacts referenced by §13.3 bundle."""
    repo_root = Path(__file__).resolve().parents[2]
    missing = [ref for ref in MANUAL_AUDIT_TRAIL if not (repo_root / ref).is_file()]
    assert not missing, f"missing manual audit refs: {missing}"


def test_golden_path_stage_sequence_matches_sor():
    """SoR §13.3 path: wave_a…wave_d → QWO-PX2-001."""
    wave_sequence = [stage.wave_id for stage in GOLDEN_PATH_STAGES]
    assert wave_sequence == ["wave_a", "wave_b", "wave_c", "wave_d"]
    qualification_stages = [stage for stage in GOLDEN_PATH_STAGES if stage.run_qualification]
    assert len(qualification_stages) == 1
    assert qualification_stages[0].integration_id == "integration-d"


def test_golden_path_rule_chain_after_plugins(tmp_path):
    """Rule engine qwo-escalate-supervisor fires after QwoPassed (4-rule pack)."""
    result = replay_px2_golden_path(tmp_path)
    assert result.passed

    engine = RuleEngine.from_pack_paths(
        [PX2_RULES],
        checkpoint={"coverage_gate": "passed"},
    )
    qwo_event = next(e for e in reversed(result.events) if e.type == "QwoSpawned")
    passed = BuildEvent(
        type="QwoPassed",
        timestamp=qwo_event.timestamp,
        payload={"qwo_id": qwo_event.payload["qwo_id"]},
        program_id=qwo_event.program_id,
        cycle_id=qwo_event.cycle_id,
    )
    descriptor = engine.evaluate(passed)
    assert isinstance(descriptor, ActionDescriptor)
    assert descriptor.rule_id == "qwo-escalate-supervisor"
    assert descriptor.plugin == "notification"


def test_golden_path_merge_order_blocks_out_of_sequence(tmp_path):
    """INV-R-03: merge_order enforced during replay stages."""
    program = load_program_graph(PX2_PROGRAM)
    bus, registry, engine, merge_plugin, _, _ = build_golden_path_runtime(tmp_path, program)
    stage = GOLDEN_PATH_STAGES[0]

    bad_stage = type(stage)(
        wave_id=stage.wave_id,
        integration_id=stage.integration_id,
        trigger_ewo_id=stage.trigger_ewo_id,
        prior_merges=(),
        manual_audit_ref=stage.manual_audit_ref,
        run_qualification=stage.run_qualification,
    )
    outcome = replay_stage(
        bad_stage,
        bus=bus,
        registry=registry,
        engine=engine,
        merge_plugin=merge_plugin,
        program=program,
    )
    assert outcome.outcome == "fail"
    assert "merge failed" in outcome.reason.lower() or "merge_order" in outcome.reason.lower()


def test_golden_path_projection_rebuild_deterministic(tmp_path):
    """INV-R-11: projection job rollup from replay is structurally deterministic."""
    first = replay_px2_golden_path(tmp_path / "run-a")
    second = replay_px2_golden_path(tmp_path / "run-b")
    assert first.passed and second.passed
    assert first.event_types == second.event_types
    assert [stage.outcome for stage in first.stages] == [
        stage.outcome for stage in second.stages
    ]
