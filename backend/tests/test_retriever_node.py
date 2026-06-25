"""Retriever node tests (M4 Phase 4)."""

from __future__ import annotations

import pytest

from app.graph.retriever import make_retriever_node
from app.schemas.graph_state import GraphState, Message
from app.schemas.retrieval import SearchResultItem
from app.services.retrieval import EmbedFailedError


class FakeRetrievalService:
    def __init__(self, *, results=None, fail=False):
        self._results = results
        self._fail = fail
        self.last_query: str | None = None

    async def search(self, query, *, filters=None, limit=10, hybrid_alpha=0.5, session=None):
        self.last_query = query
        if self._fail:
            raise EmbedFailedError("down")
        return self._results or [], "text-multilingual-embedding-002"


async def test_retriever_populates_context():
    service = FakeRetrievalService(
        results=[
            SearchResultItem(
                chunk_id="c1",
                document_id="d1",
                chunk_hash="h1",
                score=0.8,
                content="chunk text",
                document_title="Doc",
            )
        ]
    )
    node = make_retriever_node(service)
    out = await node(GraphState(messages=[Message(role="user", content="question")]))
    assert len(out["retrieved_context"]) == 1
    assert out["retrieved_context"][0].chunk_id == "c1"
    assert service.last_query == "question"


async def test_retriever_no_results_adds_error():
    node = make_retriever_node(FakeRetrievalService())
    out = await node(GraphState(messages=[Message(role="user", content="question")]))
    assert out["retrieved_context"] == []
    assert any(e.message == "no_results" for e in out["errors"])


async def test_retriever_embed_failed_adds_error():
    node = make_retriever_node(FakeRetrievalService(fail=True))
    out = await node(GraphState(messages=[Message(role="user", content="question")]))
    assert out["retrieved_context"] == []
    assert any(e.message == "embed_failed" for e in out["errors"])
