"""POST /search API tests (M4 Phase 3)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.retrieval import SearchResultItem
from app.services.retrieval import EmbedFailedError


class FakeRetrievalService:
    async def search(self, query, *, filters=None, limit=10, hybrid_alpha=0.5, session=None):
        if query == "fail":
            raise EmbedFailedError("vertex down")
        return (
            [
                SearchResultItem(
                    chunk_id="c1",
                    document_id="d1",
                    chunk_hash="abc",
                    score=0.9,
                    content="hello world",
                    document_title="Paper",
                    page_from=1,
                    page_to=1,
                )
            ],
            "text-multilingual-embedding-002",
        )


@pytest.fixture
def client(monkeypatch):
    import app.api.search as search_mod

    monkeypatch.setattr(search_mod, "_service", FakeRetrievalService())
    return TestClient(app)


def test_search_returns_ranked_results(client):
    r = client.post("/search", json={"query": "hello"})
    assert r.status_code == 200
    body = r.json()
    assert body["query_embedding_model"] == "text-multilingual-embedding-002"
    assert len(body["results"]) == 1
    assert body["results"][0]["score"] == 0.9


def test_search_empty_query_returns_400(client):
    r = client.post("/search", json={"query": "   "})
    assert r.status_code == 400
    assert r.json()["code"] == "empty_query"


def test_search_embed_failed_returns_422(client):
    r = client.post("/search", json={"query": "fail"})
    assert r.status_code == 422
    assert r.json()["code"] == "embed_failed"
