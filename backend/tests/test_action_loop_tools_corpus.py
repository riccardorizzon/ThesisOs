from __future__ import annotations

import pytest

from app.runtime.action_loop.tools.corpus import make_search_corpus_tool
from app.schemas.graph_state import RetrievedChunk
from app.schemas.retrieval import SearchResultItem
from app.services.retrieval import EmbedFailedError


class FakeRetrievalService:
    def __init__(self, *, results=None, fail=False):
        self._results = results or []
        self._fail = fail
        self.last_query: str | None = None
        self.last_limit: int | None = None
        self.last_project_id: str | None = None

    async def search(self, query, *, filters=None, limit=10, hybrid_alpha=0.5, session=None):
        self.last_query = query
        self.last_limit = limit
        self.last_project_id = getattr(filters, "project_id", None) if filters else None
        if self._fail:
            raise EmbedFailedError("embedding unavailable")
        return self._results, "fake-model"


def _search_result(
    *,
    chunk_id: str = "c1",
    content: str = "Craft is the disciplined pursuit of quality.",
) -> SearchResultItem:
    return SearchResultItem(
        chunk_id=chunk_id,
        document_id="d1",
        chunk_hash="h1",
        score=0.9,
        content=content,
        document_title="The Craftsman",
        page_from=10,
    )


@pytest.mark.asyncio
async def test_search_corpus_returns_chunk_summaries():
    service = FakeRetrievalService(results=[_search_result()])
    accumulate: list[RetrievedChunk] = []
    search_corpus = make_search_corpus_tool(
        retrieval_service=service,
        project_id="p1",
        accumulate=accumulate,
    )

    result = await search_corpus("craftsmanship")

    assert service.last_query == "craftsmanship"
    assert service.last_project_id == "p1"
    assert result["count"] == 1
    assert result["chunks"][0]["chunk_id"] == "c1"
    assert result["chunks"][0]["document_title"] == "The Craftsman"
    assert len(accumulate) == 1
    assert accumulate[0].chunk_id == "c1"


@pytest.mark.asyncio
async def test_search_corpus_dedupes_accumulated_chunks():
    service = FakeRetrievalService(
        results=[
            _search_result(chunk_id="c1"),
            _search_result(chunk_id="c1", content="duplicate"),
        ]
    )
    accumulate: list[RetrievedChunk] = [
        RetrievedChunk(chunk_id="c0", score=0.5, content="existing")
    ]
    search_corpus = make_search_corpus_tool(
        retrieval_service=service,
        project_id=None,
        accumulate=accumulate,
    )

    await search_corpus("craft")

    assert len(accumulate) == 2
    assert [chunk.chunk_id for chunk in accumulate] == ["c0", "c1"]


@pytest.mark.asyncio
async def test_search_corpus_caps_limit_at_10():
    service = FakeRetrievalService(results=[_search_result()])
    accumulate: list[RetrievedChunk] = []
    search_corpus = make_search_corpus_tool(
        retrieval_service=service,
        project_id=None,
        accumulate=accumulate,
    )

    await search_corpus("craft", limit=25)

    assert service.last_limit == 10


@pytest.mark.asyncio
async def test_search_corpus_coerces_string_limit_from_llm():
    """Vertex/tool JSON often emits limit as a string — must not TypeError on min()."""
    service = FakeRetrievalService(results=[_search_result()])
    accumulate: list[RetrievedChunk] = []
    search_corpus = make_search_corpus_tool(
        retrieval_service=service,
        project_id=None,
        accumulate=accumulate,
    )

    await search_corpus("craft", limit="5")  # type: ignore[arg-type]

    assert service.last_limit == 5


@pytest.mark.asyncio
async def test_search_corpus_skips_duplicate_across_calls():
    service = FakeRetrievalService(results=[_search_result(chunk_id="c1")])
    accumulate: list[RetrievedChunk] = []
    search_corpus = make_search_corpus_tool(
        retrieval_service=service,
        project_id=None,
        accumulate=accumulate,
    )

    await search_corpus("first query")
    await search_corpus("second query")

    assert len(accumulate) == 1
