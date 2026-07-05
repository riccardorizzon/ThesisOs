"""Knowledge Object API tests (PX3-EWO-001)."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_knowledge_objects_defaults():
    res = client.get("/projects/thesis-agent/knowledge/objects")
    assert res.status_code == 200
    body = res.json()
    assert body["total"] >= 5
    types = {o["type"] for o in body["objects"]}
    assert "concept" in types
    assert "source" in types
    assert all("knowledge_state" in o for o in body["objects"])


def test_list_knowledge_objects_sources_only():
    res = client.get(
        "/projects/thesis-agent/knowledge/objects",
        params={"type": "source"},
    )
    assert res.status_code == 200
    body = res.json()
    assert all(o["type"] == "source" for o in body["objects"])
    ids = {o["id"] for o in body["objects"]}
    assert "barthes-mythologies" not in ids


def test_list_knowledge_objects_include_deprecated():
    res = client.get(
        "/projects/thesis-agent/knowledge/objects",
        params={"type": "source", "include_deprecated": "true"},
    )
    ids = {o["id"] for o in res.json()["objects"]}
    assert "barthes-mythologies" in ids
    deprecated = next(o for o in res.json()["objects"] if o["id"] == "barthes-mythologies")
    assert deprecated["knowledge_state"] == "deprecated"


def test_get_knowledge_object_concept():
    res = client.get("/projects/thesis-agent/knowledge/objects/aura")
    assert res.status_code == 200
    body = res.json()
    assert body["type"] == "concept"
    assert body["slug"] == "aura"
    assert body["is_core"] is True
    assert body["linked_counts"]["sources"] == 1


def test_get_knowledge_object_not_found():
    res = client.get("/projects/thesis-agent/knowledge/objects/missing-slug")
    assert res.status_code == 404
    assert res.json()["code"] == "knowledge_object_not_found"
