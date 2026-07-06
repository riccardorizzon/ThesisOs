"""Knowledge search API tests."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
PROJECT = "thesis-agent"


def test_search_knowledge_aura():
    res = client.get(f"/projects/{PROJECT}/knowledge/search", params={"q": "aura"})
    assert res.status_code == 200
    body = res.json()
    assert body["total"] >= 1
    assert any(r["slug"] == "aura" for r in body["results"])


def test_search_knowledge_empty_query_rejected():
    res = client.get(f"/projects/{PROJECT}/knowledge/search", params={"q": ""})
    assert res.status_code == 422
