"""Knowledge Graph tests (PX3-EWO-009, px3-knowledge-experience-v2 §10)."""

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.knowledge_graph import DEFAULT_VISIBLE_NODES, HARD_NODE_LIMIT
from app.services.knowledge.graph import build_knowledge_graph

client = TestClient(app)


def test_knowledge_graph_default_limit():
    res = client.get("/projects/thesis-agent/knowledge/graph")
    assert res.status_code == 200
    body = res.json()
    assert body["schema_version"] == 1
    assert body["limits"]["default_visible"] == DEFAULT_VISIBLE_NODES
    assert body["limits"]["visible_count"] <= DEFAULT_VISIBLE_NODES
    assert body["limits"]["hard_limit"] == HARD_NODE_LIMIT


def test_knowledge_graph_focus_and_depth():
    graph = build_knowledge_graph(focus_slug="aura", depth=1, max_nodes=15)
    slugs = {node.slug for node in graph.nodes}
    assert "aura" in slugs
    assert graph.focus_slug == "aura"
    assert graph.depth == 1


def test_knowledge_graph_nodes_have_lifecycle_state():
    body = client.get("/projects/thesis-agent/knowledge/graph?focus=stigmata&depth=1").json()
    for node in body["nodes"]:
        assert node["knowledge_state"] in {
            "candidate",
            "validated",
            "linked",
            "referenced",
            "deprecated",
        }


def test_knowledge_graph_hard_limit_forces_list_view():
    graph = build_knowledge_graph(max_nodes=HARD_NODE_LIMIT, force_list=True)
    assert graph.view_mode == "list"
    assert graph.limits.force_list_view is True


def test_knowledge_graph_edges_only_among_visible_nodes():
    body = client.get("/projects/thesis-agent/knowledge/graph?focus=stigmata&depth=2").json()
    slugs = {node["slug"] for node in body["nodes"]}
    for edge in body["edges"]:
        assert edge["source"] in slugs
        assert edge["target"] in slugs


def test_knowledge_graph_read_only():
    post = client.post("/projects/thesis-agent/knowledge/graph")
    assert post.status_code == 405


def test_knowledge_graph_canvas_profile_includes_satellites():
    body = client.get(
        "/projects/thesis-agent/knowledge/graph?profile=canvas&focus=stigmata&depth=2"
    ).json()
    kinds = {node["kind"] for node in body["nodes"]}
    assert "concept" in kinds
    assert "source" in kinds
    assert body["limits"]["default_visible"] == 80
    assert body["limits"]["hard_limit"] == 300
    slugs = {node["slug"] for node in body["nodes"]}
    for edge in body["edges"]:
        assert edge["source"] in slugs
        assert edge["target"] in slugs
    link_kinds = {edge.get("link_kind") for edge in body["edges"] if edge.get("link_kind")}
    assert "concept_source" in link_kinds
