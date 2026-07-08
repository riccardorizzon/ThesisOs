"""Knowledge search API tests."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
PROJECT = "thesis-agent"


@pytest.mark.asyncio
async def test_search_knowledge_aura(db_session):
    client.post(
        f"/projects/{PROJECT}/knowledge/concepts",
        json={"slug": "aura", "title": "Aura", "summary": "Benjamin aura concept"},
    )
    res = client.get(f"/projects/{PROJECT}/knowledge/search", params={"q": "aura"})
    assert res.status_code == 200
    body = res.json()
    assert body["total"] >= 1
    assert any(r["slug"] == "aura" for r in body["results"])


def test_search_knowledge_empty_query_rejected():
    res = client.get(f"/projects/{PROJECT}/knowledge/search", params={"q": ""})
    assert res.status_code == 422
