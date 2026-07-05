"""Execution Graph observation tests (PX3-EWO-008, SoR §4.2)."""

from fastapi.testclient import TestClient

from app.main import app
from app.services.conformance.program_graph import (
    build_program_graph_observation,
    repo_root,
)

client = TestClient(app)

_FORBIDDEN_SCHEDULING_KEYS = frozenset(
    {
        "ready_set",
        "ready_jobs",
        "critical_path",
        "dispatch",
        "ready",
    }
)


def test_program_graph_schema_v1():
    res = client.get("/projects/thesis-agent/conformance/program-graph")
    assert res.status_code == 200
    body = res.json()
    assert body["schema_version"] == 1
    assert body["program_id"] == "px3-parallel"
    assert body["source"] == ".asep/programs/px3-parallel.yaml"
    assert len(body["waves"]) >= 9
    wave_ids = {w["wave_id"] for w in body["waves"]}
    assert "wave_c_execution_graph" in wave_ids
    assert "PX3-EWO-008" in {
        n["node_id"] for w in body["waves"] for n in w["nodes"]
    }


def test_program_graph_wave_dag_edges():
    body = client.get("/projects/thesis-agent/conformance/program-graph").json()
    depends_edges = [
        e for e in body["edges"] if e["edge_type"] == "depends_on_wave"
    ]
    assert depends_edges
    wave_a_core = next(w for w in body["waves"] if w["wave_id"] == "wave_a_core")
    assert wave_a_core["merge_order"] == ["PX3-EWO-002", "PX3-EWO-003"]
    merge_edges = [e for e in body["edges"] if e["edge_type"] == "merge_order"]
    assert any(
        e["source"] == "PX3-EWO-002" and e["target"] == "PX3-EWO-003"
        for e in merge_edges
    )


def test_program_graph_read_only_get_only():
    post = client.post("/projects/thesis-agent/conformance/program-graph")
    assert post.status_code == 405


def test_program_graph_does_not_compute_ready_set():
    """INV-R-12 — observability must not expose scheduling derivation."""
    body = client.get("/projects/thesis-agent/conformance/program-graph").json()
    assert _FORBIDDEN_SCHEDULING_KEYS.isdisjoint(body.keys())
    for wave in body["waves"]:
        assert _FORBIDDEN_SCHEDULING_KEYS.isdisjoint(wave.keys())
        for node in wave["nodes"]:
            assert _FORBIDDEN_SCHEDULING_KEYS.isdisjoint(node.keys())
    for edge in body["edges"]:
        assert _FORBIDDEN_SCHEDULING_KEYS.isdisjoint(edge.keys())


def test_program_graph_nodes_trace_to_yaml():
    """INV-R-01 — every node maps 1:1 to Program Graph workorder declaration."""
    graph = build_program_graph_observation(root=repo_root())
    yaml_workorders: set[str] = set()
    for wave in graph.waves:
        yaml_workorders.update(wave.workorders)
    observed = {node.node_id for wave in graph.waves for node in wave.nodes}
    assert observed == yaml_workorders
    assert len(observed) == len(yaml_workorders)


def test_program_graph_rebuild_is_deterministic():
    first = build_program_graph_observation().model_dump(mode="json")
    second = build_program_graph_observation().model_dump(mode="json")
    assert first == second
