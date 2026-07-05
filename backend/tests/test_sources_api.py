"""Sources module API tests (PX3-EWO-002)."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_sources_default_omits_deprecated():
    res = client.get("/projects/thesis-agent/sources")
    assert res.status_code == 200
    body = res.json()
    ids = {s["id"] for s in body["sources"]}
    assert "barthes-mythologies" not in ids
    assert "benjamin-opera-arte" in ids


def test_list_sources_include_related_concepts():
    res = client.get("/projects/thesis-agent/sources")
    benjamin = next(
        s for s in res.json()["sources"] if s["id"] == "benjamin-opera-arte"
    )
    assert len(benjamin["related_concepts"]) >= 1
    assert benjamin["related_concepts"][0]["slug"] == "aura"


def test_list_sources_search():
    res = client.get(
        "/projects/thesis-agent/sources",
        params={"q": "Benjamin"},
    )
    assert res.status_code == 200
    assert len(res.json()["sources"]) == 1


def test_list_sources_filter_state():
    res = client.get(
        "/projects/thesis-agent/sources",
        params={"state": "linked", "include_deprecated": "true"},
    )
    assert res.status_code == 200
    assert all(s["knowledge_state"] == "linked" for s in res.json()["sources"])
