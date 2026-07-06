"""MB2-Q1 — Runtime Graph qualification tests (normative test IDs).

SoR §13.2 MB2-Q1: Program Graph → Execution Graph; illegal node rejected;
MB2-Q-001…003.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from builder_engine.dependency import DependencyEngine
from builder_engine.job_queue import Job, job_transition
from builder_engine.program_graph import (
    ProgramGraph,
    WorkOrderNode,
    load_program_graph,
    load_program_graph_from_repo,
    validate_program_graph,
)
from builder_engine.state_machine import ExecutionState


def _fixtures_dir() -> Path:
    return Path(__file__).resolve().parent / "fixtures"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_mb2_q_001_execution_graph_derived_only_from_program_graph():
    program = load_program_graph_from_repo(_repo_root(), "px-exec")
    engine = DependencyEngine(program)
    graph = engine.derive(publish=False)

    assert set(graph.nodes) == set(program.workorders)
    for ewo_id, node in graph.nodes.items():
        assert node.program_graph_ref == ewo_id
        assert node.depends_on == program.workorders[ewo_id].depends_on

    engine_alt = DependencyEngine(
        program,
        completion_state={ewo_id: "implemented" for ewo_id in program.workorders},
    )
    alt_graph = engine_alt.derive(publish=False)
    assert set(alt_graph.nodes) == set(graph.nodes)
    assert engine_alt.ready_set(alt_graph) == []


def test_mb2_q_001_illegal_program_graph_rejected():
    with pytest.raises(ValueError, match="circular"):
        load_program_graph(_fixtures_dir() / "px_exec_program_circular.yaml")


def test_mb2_q_001_job_fsm_legal_transitions_req_14():
    job = Job(
        job_id="PX-EXEC-EWO-002",
        program_id="px-exec",
        ewo_id="PX-EXEC-EWO-002",
        state=ExecutionState.READY,
    )
    job = job_transition(job, "claim")
    assert job.state == ExecutionState.CLAIMED
    job = job_transition(job, "abort_claim")
    assert job.state == ExecutionState.READY


def test_mb2_q_002_no_orphan_executable_nodes():
    graph = ProgramGraph(
        program_id="orphan-test",
        workorders={
            "A": WorkOrderNode(id="A", depends_on=("missing-ref",)),
        },
        waves={},
    )
    with pytest.raises(ValueError, match="unknown dependency"):
        validate_program_graph(graph)

    program = load_program_graph(_fixtures_dir() / "px_exec_program_minimal.yaml")
    derived = DependencyEngine(program).derive(publish=False)
    for node in derived.nodes.values():
        assert node.program_graph_ref in program.workorders


def test_mb2_q_003_merge_order_respected():
    program = load_program_graph(_fixtures_dir() / "px2_parallel_program_excerpt.yaml")
    engine = DependencyEngine(program)
    graph = engine.derive(publish=False)
    ready_ids = [n.ewo_id for n in engine.ready_set(graph)]
    assert ready_ids == ["PX2-EWO-003", "PX2-EWO-004", "PX2-EWO-006"]
    assert program.waves["wave_b"].merge_order == tuple(ready_ids)

    deps_before = {n.ewo_id: n.depends_on for n in graph.nodes.values()}
    wave = program.waves["wave_b"]
    reordered = ProgramGraph(
        program_id=program.program_id,
        workorders=program.workorders,
        waves={
            "wave_b": type(wave)(
                id=wave.id,
                workorders=wave.workorders,
                merge_order=("PX2-EWO-006", "PX2-EWO-004", "PX2-EWO-003"),
                execute_in_parallel=wave.execute_in_parallel,
            )
        },
    )
    engine2 = DependencyEngine(reordered)
    graph2 = engine2.derive(publish=False)
    ready_reordered = [n.ewo_id for n in engine2.ready_set(graph2)]
    assert ready_reordered == ["PX2-EWO-006", "PX2-EWO-004", "PX2-EWO-003"]
    deps_after = {n.ewo_id: n.depends_on for n in graph2.nodes.values()}
    assert deps_before == deps_after


def test_mb2_q_003_px_exec_wave_merge_order():
    program = load_program_graph(_fixtures_dir() / "px_exec_program_minimal.yaml")
    engine = DependencyEngine(program)
    graph = engine.derive(publish=False)
    ready = [n.ewo_id for n in engine.ready_set(graph)]
    assert ready == ["PX-EXEC-EWO-003", "PX-EXEC-EWO-002"]
    assert ready == list(program.waves["wave_a"].merge_order[:2])
