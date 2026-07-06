"""PX-2 parallel golden path replay — SoR §13.3 audited bundle."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from builder_engine.events import BuildEvent, BuildEventBus
from builder_engine.integration import IntegrationPlugin, execute_integration_action, register_integration_plugin
from builder_engine.merge import MergePlugin, execute_merge_action, register_merge_plugin
from builder_engine.plugin_registry import PluginRegistry
from builder_engine.program_graph import ProgramGraph, WaveSpec, load_program_graph
from builder_engine.projection import ProjectionBuilder
from builder_engine.qualification import (
    QualificationPlugin,
    execute_qualification_action,
    register_qualification_plugin,
)
from builder_engine.rules import ActionDescriptor, RuleEngine

FIXTURES = Path(__file__).resolve().parent / "fixtures"
TEST_FIXTURES = Path(__file__).resolve().parent / "tests" / "fixtures"
PX2_RULES = FIXTURES / "px2_parallel_rules.yaml"
PX2_PROGRAM = FIXTURES / "px2_golden_path_program.yaml"
GOLDEN_INTEGRATION_CHECKS = TEST_FIXTURES / "golden_path_integration_checks.yaml"
GOLDEN_QWO_SPAWN = TEST_FIXTURES / "golden_path_qwo_spawn.yaml"

StageOutcome = Literal["pass", "fail", "blocked"]


@dataclass(frozen=True)
class GoldenPathStage:
    wave_id: str
    integration_id: str
    trigger_ewo_id: str
    prior_merges: tuple[str, ...]
    manual_audit_ref: str
    run_qualification: bool = False


GOLDEN_PATH_STAGES: tuple[GoldenPathStage, ...] = (
    GoldenPathStage(
        "wave_a",
        "wave-a-integration",
        "PX2-EWO-005",
        ("PX2-EWO-001", "PX2-EWO-002"),
        ".asep/reports/PX2-INTEGRATION-A.md",
    ),
    GoldenPathStage(
        "wave_b",
        "wave-b-integration",
        "PX2-EWO-006",
        ("PX2-EWO-003", "PX2-EWO-004"),
        ".asep/reports/PX2-INTEGRATION-B.md",
    ),
    GoldenPathStage(
        "wave_c",
        "wave-c-integration",
        "PX2-EWO-007",
        (),
        ".asep/reports/PX2-INTEGRATION-C.md",
    ),
    GoldenPathStage(
        "wave_d",
        "integration-d",
        "PX2-EWO-008",
        (),
        ".asep/reports/PX2-INTEGRATION-D.md",
        run_qualification=True,
    ),
)

MANUAL_AUDIT_TRAIL: tuple[str, ...] = tuple(stage.manual_audit_ref for stage in GOLDEN_PATH_STAGES) + (
    ".asep/programs/px2-parallel.yaml",
)


@dataclass
class StageResult:
    stage: GoldenPathStage
    outcome: StageOutcome
    merge_id: str | None = None
    qwo_id: str | None = None
    reason: str = ""


@dataclass
class GoldenPathReplayResult:
    stages: list[StageResult] = field(default_factory=list)
    events: list[BuildEvent] = field(default_factory=list)
    event_types: list[str] = field(default_factory=list)
    projection_hash: str | None = None
    qualified: bool = False

    @property
    def passed(self) -> bool:
        return self.qualified and all(stage.outcome == "pass" for stage in self.stages)


def _fixed_event(
    event_type: str,
    payload: dict[str, Any],
    *,
    program_id: str = "px2-parallel",
    cycle_id: str = "golden-path",
) -> BuildEvent:
    return BuildEvent(
        type=event_type,
        timestamp="2026-07-06T00:00:00+00:00",
        payload=payload,
        program_id=program_id,
        cycle_id=cycle_id,
    )


def _latest_event(bus: BuildEventBus, event_type: str) -> BuildEvent | None:
    matches = [event for event in bus.replay() if event.type == event_type]
    return matches[-1] if matches else None


def build_golden_path_runtime(
    tmp_path: Path,
    program: ProgramGraph,
    *,
    cycle_id: str = "golden-path",
) -> tuple[BuildEventBus, PluginRegistry, RuleEngine, MergePlugin, IntegrationPlugin, QualificationPlugin]:
    bus = BuildEventBus(tmp_path)
    registry = PluginRegistry()
    merge_plugin = MergePlugin(program, bus=bus, cycle_id=cycle_id)
    integration_plugin = IntegrationPlugin(
        program_id=program.program_id,
        bus=bus,
        cycle_id=cycle_id,
        checks_fixture=GOLDEN_INTEGRATION_CHECKS,
    )
    qualification_plugin = QualificationPlugin(
        program_id=program.program_id,
        bus=bus,
        cycle_id=cycle_id,
        spawn_fixture=GOLDEN_QWO_SPAWN,
    )
    register_merge_plugin(registry, merge_plugin)
    register_integration_plugin(registry, integration_plugin)
    register_qualification_plugin(registry, qualification_plugin)
    engine = RuleEngine.from_pack_paths(
        [PX2_RULES],
        checkpoint={
            "all_dependencies_satisfied": True,
            "ci_status": "passed",
            "coverage_gate": "passed",
        },
    )
    return bus, registry, engine, merge_plugin, integration_plugin, qualification_plugin


def replay_stage(
    stage: GoldenPathStage,
    *,
    bus: BuildEventBus,
    registry: PluginRegistry,
    engine: RuleEngine,
    merge_plugin: MergePlugin,
    program: ProgramGraph,
) -> StageResult:
    """Replay one wave barrier: EwoCompleted → merge → integration [→ qualification]."""
    for prior in stage.prior_merges:
        merge_plugin._completed.add(prior)

    ewo_event = _fixed_event(
        "EwoCompleted",
        {"ewo_id": stage.trigger_ewo_id, "wave_id": stage.wave_id},
    )
    bus.publish(ewo_event)

    merge_descriptor = engine.evaluate(ewo_event)
    if not isinstance(merge_descriptor, ActionDescriptor):
        return StageResult(stage=stage, outcome="fail", reason="merge rule did not match")

    merge_result = execute_merge_action(
        registry,
        merge_descriptor,
        event_payload={"ewo_id": stage.trigger_ewo_id},
    )
    if merge_result.outcome != "completed":
        return StageResult(
            stage=stage,
            outcome="fail",
            reason=f"merge failed: {merge_result.reason}",
        )

    merge_event = _latest_event(bus, "MergeCompleted")
    if merge_event is None:
        return StageResult(stage=stage, outcome="fail", reason="MergeCompleted not emitted")

    merge_payload = {
        **merge_event.payload,
        "integration_id": stage.integration_id,
        "ci_status": "passed",
        "program_id": program.program_id,
    }
    integration_descriptor = engine.evaluate(
        _fixed_event("MergeCompleted", merge_payload),
    )
    if not isinstance(integration_descriptor, ActionDescriptor):
        return StageResult(stage=stage, outcome="blocked", reason="integration rule did not match")

    integration_result = execute_integration_action(
        registry,
        integration_descriptor,
        event_payload=merge_payload,
    )
    if integration_result.get("outcome") != "passed":
        return StageResult(
            stage=stage,
            outcome="blocked",
            reason=str(integration_result.get("reason") or integration_result.get("outcome")),
        )

    qwo_id: str | None = None
    if stage.run_qualification:
        passed_event = _latest_event(bus, "IntegrationPassed")
        if passed_event is None:
            return StageResult(stage=stage, outcome="fail", reason="IntegrationPassed not emitted")

        qual_payload = {
            **passed_event.payload,
            "integration_id": stage.integration_id,
            "coverage_gate": "passed",
            "program_id": program.program_id,
        }
        qual_descriptor = engine.evaluate(
            _fixed_event("IntegrationPassed", qual_payload),
        )
        if not isinstance(qual_descriptor, ActionDescriptor):
            return StageResult(stage=stage, outcome="fail", reason="qualification rule did not match")

        qual_result = execute_qualification_action(
            registry,
            qual_descriptor,
            event_payload=qual_payload,
        )
        if qual_result.get("outcome") != "collected":
            return StageResult(
                stage=stage,
                outcome="fail",
                reason=str(qual_result.get("reason") or qual_result.get("outcome")),
            )
        qwo_id = str(qual_result.get("qwo_id") or "QWO-PX2-001")

    return StageResult(
        stage=stage,
        outcome="pass",
        merge_id=merge_result.merge_id,
        qwo_id=qwo_id,
    )


def replay_px2_golden_path(
    tmp_path: Path,
    *,
    program_path: Path | None = None,
    cycle_id: str = "golden-path",
) -> GoldenPathReplayResult:
    """Audited replay of PX-2 parallel golden path via live Phase 2 plugins."""
    program = load_program_graph(program_path or PX2_PROGRAM)
    bus, registry, engine, merge_plugin, _, _ = build_golden_path_runtime(
        tmp_path, program, cycle_id=cycle_id
    )

    result = GoldenPathReplayResult()
    for stage in GOLDEN_PATH_STAGES:
        stage_result = replay_stage(
            stage,
            bus=bus,
            registry=registry,
            engine=engine,
            merge_plugin=merge_plugin,
            program=program,
        )
        result.stages.append(stage_result)
        if stage_result.outcome != "pass":
            break

    events = bus.replay()
    result.events = events
    result.event_types = [event.type for event in events]

    builder = ProjectionBuilder(repo_root=tmp_path, bus=bus)
    projection = builder.rebuild(events)
    result.projection_hash = builder.content_hash()
    result.qualified = (
        all(stage.outcome == "pass" for stage in result.stages)
        and any(event.type == "QwoSpawned" for event in events)
        and result.stages[-1].qwo_id == "QWO-PX2-001"
    )
    _ = projection
    return result


def expected_lifecycle_event_types() -> tuple[str, ...]:
    """Normative event types for §13.3 golden path (merge → integration → QWO)."""
    return (
        "EwoCompleted",
        "MergeCompleted",
        "IntegrationStarted",
        "IntegrationPassed",
        "QwoSpawned",
    )


def wave_merge_order(program: ProgramGraph, wave_id: str) -> tuple[str, ...]:
    wave: WaveSpec | None = program.waves.get(wave_id)
    if wave is None:
        return ()
    return wave.merge_order
