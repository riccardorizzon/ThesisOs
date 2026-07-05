"""Supervisor Interaction Observation tests (PX3-EWO-006)."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_concept_header_endpoint():
    res = client.get("/projects/thesis-agent/knowledge/concepts/aura/header")
    assert res.status_code == 200
    body = res.json()
    assert body["slug"] == "aura"
    assert body["title"] == "Aura"
    assert "definition" not in body


def test_concept_definition_endpoint():
    res = client.get("/projects/thesis-agent/knowledge/concepts/aura/definition")
    assert res.status_code == 200
    body = res.json()
    assert body["slug"] == "aura"
    assert body["definition"] is not None
    assert body["source_count"] == 1


def test_concept_header_not_found():
    res = client.get("/projects/thesis-agent/knowledge/concepts/missing/header")
    assert res.status_code == 404
