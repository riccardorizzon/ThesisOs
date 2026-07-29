"""Author/document retrieval boost — prefer primary books over secondary mentions."""

from __future__ import annotations

from app.graph.corpus_query import author_document_boost_queries
from app.graph.retriever import make_retriever_node
from app.schemas.graph_state import GraphState, Message
from app.schemas.retrieval import SearchResultItem


def test_author_boost_sennett_query():
    from app.graph.corpus_query import author_document_boosts

    boosts = author_document_boosts(
        "Secondo Sennett, cosa distingue craftsmanship dal lavoro astratto?"
    )
    assert boosts
    assert any("Craftsman" in q or "workmanship" in q for q, _title in boosts)
    assert any(title == "Sennett_The-Craftsman" for _q, title in boosts)


def test_author_boost_no_match_on_generic_query():
    assert author_document_boost_queries("Cos'è STIGMATA nel corpus?") == []


class _RecordingRetrievalService:
    def __init__(self) -> None:
        self.queries: list[str] = []

    async def search(self, query, *, filters=None, limit=10, hybrid_alpha=0.5, session=None):
        self.queries.append(query)
        if "Craftsman" in query or "workmanship" in query:
            title = "Sennett_The-Craftsman"
        else:
            title = "Core-Theory-Map"
        return (
            [
                SearchResultItem(
                    chunk_id=f"c-{len(self.queries)}",
                    document_id="d1",
                    chunk_hash="h1",
                    score=0.9,
                    content="chunk",
                    document_title=title,
                )
            ],
            "text-multilingual-embedding-002",
        )


async def test_retriever_runs_author_boost_search():
    service = _RecordingRetrievalService()
    node = make_retriever_node(service)
    out = await node(
        GraphState(
            messages=[
                Message(
                    role="user",
                    content="Secondo Sennett, cosa distingue la pratica manuale?",
                )
            ]
        ),
        {"configurable": {"project_id": "thesis-agent"}},
    )
    assert any("Craftsman" in q or "workmanship" in q for q in service.queries)
    titles = [c.document_title for c in out["retrieved_context"]]
    assert "Sennett_The-Craftsman" in titles


async def test_retriever_filters_boost_hits_to_primary_title():
    class _MixedService:
        async def search(self, query, *, filters=None, limit=10, hybrid_alpha=0.5, session=None):
            return (
                [
                    SearchResultItem(
                        chunk_id="c-core",
                        document_id="d-core",
                        chunk_hash="h1",
                        score=0.99,
                        content="mentions Sennett",
                        document_title="Core-Theory-Map",
                    ),
                    SearchResultItem(
                        chunk_id="c-sennett",
                        document_id="d-sennett",
                        chunk_hash="h2",
                        score=0.5,
                        content="The Craftsman",
                        document_title="Sennett_The-Craftsman",
                    ),
                ],
                "text-multilingual-embedding-002",
            )

    node = make_retriever_node(_MixedService())
    out = await node(
        GraphState(
            messages=[Message(role="user", content="Secondo Sennett, craftsmanship?")]
        ),
        {"configurable": {"project_id": "thesis-agent"}},
    )
    # Boost layer must surface Sennett book before Core-Theory mentions.
    assert out["retrieved_context"][0].document_title == "Sennett_The-Craftsman"