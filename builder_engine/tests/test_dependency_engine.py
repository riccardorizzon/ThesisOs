from __future__ import annotations

from pathlib import Path

import pytest

from builder_engine.dependency import DependencyEngine
from builder_engine.events import BuildEventBus
from builder_engine.graph import BuilderGraph
from builder_engine.program_graph import (
    ProgramGraph,
    WorkOrderNode,
    load_program_graph,
    validate_program_graph,
)
from builder_engine.scheduler import compute_ready


def _fixtures_dir() -> Path:
    return Path(__file__).resolve().parent / "fixtures"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_program_graph_loads_px_exec_backlog():
    graph = load_program_graph(_fixtures_dir() / "px_exec_program_minimal.yaml")
    assert graph.program_id == "px-exec-test"
    assert set(graph.workorders) == {
        "PX-EXEC-EWO-001",
        "PX-EXEC-EWO-002",
        "PX-EXEC-EWO-003",
        "PX-EXEC-EWO-004",
    }
    assert graph.waves["wave_a"].merge_order == (
        "PX-EXEC-EWO-003",
        "PX-EXEC-EWO-002",
        "PX-EXEC-EWO-004",
    )


def test_derive_only_from_program_graph():
    program = load_program_graph(_fixtures_dir() / "px_exec_program_minimal.yaml")
    engine = DependencyEngine(program)
    graph = engine.derive(publish=False)

    assert set(graph.nodes) == set(program.workorders)
    ready_ids = [n.ewo_id for n in engine.ready_set(graph)]
    assert ready_ids == ["PX-EXEC-EWO-003", "PX-EXEC-EWO-002"]

    engine_blocked = DependencyEngine(
        program,
        completion_state={"PX-EXEC-EWO-001": "ready"},
    )
    blocked_graph = engine_blocked.derive(publish=False)
    blocked_ready = [n.ewo_id for n in engine_blocked.ready_set(blocked_graph)]
    assert "PX-EXEC-EWO-002" not in blocked_ready
    assert "PX-EXEC-EWO-003" not in blocked_ready
    assert blocked_ready == ["PX-EXEC-EWO-001"]


def test_no_orphan_nodes():
    graph = ProgramGraph(
        program_id="orphan-test",
        workorders={
            "A": WorkOrderNode(id="A", depends_on=("missing",)),
        },
        waves={},
    )
    with pytest.raises(ValueError, match="unknown dependency"):
        validate_program_graph(graph)


def test_merge_order_tiebreak_only():
    program = load_program_graph(_fixtures_dir() / "px2_parallel_program_excerpt.yaml")
    engine = DependencyEngine(program)
    graph = engine.derive(publish=False)

    first_order = [n.ewo_id for n in engine.ready_set(graph)]
    assert first_order == ["PX2-EWO-003", "PX2-EWO-004", "PX2-EWO-006"]

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
    second_order = [n.ewo_id for n in engine2.ready_set(graph2)]
    assert second_order == ["PX2-EWO-006", "PX2-EWO-004", "PX2-EWO-003"]

    for node in graph.nodes.values():
        assert node.depends_on == graph2.nodes[node.ewo_id].depends_on


def test_blocked_until_deps_done():
    program = load_program_graph(_fixtures_dir() / "px_exec_program_minimal.yaml")
    engine = DependencyEngine(program)
    graph = engine.derive(publish=False)

    ewo004 = graph.nodes["PX-EXEC-EWO-004"]
    assert ewo004.state == "blocked"
    assert not ewo004.ready

    engine_done = DependencyEngine(
        program,
        completion_state={
            "PX-EXEC-EWO-001": "implemented",
            "PX-EXEC-EWO-003": "implemented",
            "PX-EXEC-EWO-004": "ready",
        },
    )
    done_graph = engine_done.derive(publish=False)
    assert done_graph.nodes["PX-EXEC-EWO-004"].ready


def test_execution_graph_derived_event(tmp_path):
    program = load_program_graph(_fixtures_dir() / "px_exec_program_minimal.yaml")
    bus = BuildEventBus(tmp_path)
    engine = DependencyEngine(program, bus=bus, cycle_id="test-cycle")
    graph = engine.derive()

    events = bus.tail(1)
    assert len(events) == 1
    event = events[0]
    assert event.type == "ExecutionGraphDerived"
    assert event.program_id == "px-exec-test"
    assert event.cycle_id == "test-cycle"
    assert event.payload["graph_hash"] == graph.graph_hash
    assert event.payload["ready_count"] == 2
    assert set(event.payload["node_ids"]) == set(program.workorders)


def test_parallel_wave_ready_set():
    program = load_program_graph(_fixtures_dir() / "px2_parallel_program_excerpt.yaml")
    engine = DependencyEngine(program)
    graph = engine.derive(publish=False)
    ready = engine.ready_set(graph)
    assert len(ready) == 3
    assert program.waves["wave_b"].execute_in_parallel is True


def test_illegal_program_graph_rejected():
    with pytest.raises(ValueError, match="circular"):
        load_program_graph(_fixtures_dir() / "px_exec_program_circular.yaml")


def test_px2_merge_order_excerpt():
    program = load_program_graph(_fixtures_dir() / "px2_parallel_program_excerpt.yaml")
    engine = DependencyEngine(program)
    graph = engine.derive(publish=False)
    assert [n.ewo_id for n in engine.ready_set(graph)] == [
        "PX2-EWO-003",
        "PX2-EWO-004",
        "PX2-EWO-006",
    ]


def test_era_i_compute_ready_parity_documented():
    """Bridge test: wave-1 ready packets align with Program Graph mapping."""
    builder = BuilderGraph.load(_repo_root() / "plans" / "builder" / "STATE.example.yaml")
    era_ready = {p.id for p in compute_ready(builder)}

    program = ProgramGraph(
        program_id="state-example-bridge",
        workorders={
            pid: WorkOrderNode(
                id=pid,
                depends_on=packet.depends_on,
                status=packet.status,
                wave=f"wave_{packet.wave}",
            )
            for pid, packet in builder.packets.items()
        },
        waves={},
    )
    engine = DependencyEngine(program)
    graph = engine.derive(publish=False)
    pg_ready = {n.ewo_id for n in engine.ready_set(graph) if n.wave == "wave_1"}

    assert pg_ready == era_ready


def test_every_execution_node_traces_to_program_graph():
    program = load_program_graph(_fixtures_dir() / "px_exec_program_minimal.yaml")
    graph = DependencyEngine(program).derive(publish=False)
    for node in graph.nodes.values():
        assert node.program_graph_ref in program.workorders
        assert node.program_graph_ref == node.ewo_id


def test_graph_hash_stable():
    program = load_program_graph(_fixtures_dir() / "px_exec_program_minimal.yaml")
    g1 = DependencyEngine(program).derive(publish=False)
    g2 = DependencyEngine(program).derive(publish=False)
    assert g1.graph_hash == g2.graph_hash
