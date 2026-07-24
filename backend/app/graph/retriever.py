"""Retriever LangGraph node — populates GraphState.retrieved_context (M4)."""

from __future__ import annotations

from app.graph.corpus_query import (
    CORPUS_LIST_BOOST_QUERY,
    CORPUS_RETRIEVAL_LIMIT,
    EXCLUSION_BOOST_QUERY,
    is_corpus_list_query,
)
from langchain_core.runnables import RunnableConfig

from app.schemas.graph_state import AgentError, GraphState, Message, RetrievedChunk
from app.schemas.retrieval import SearchFilters, SearchResultItem
from app.services.retrieval import EmbedFailedError, RetrievalService


def _last_user_message(messages: list[Message]) -> str | None:
    for message in reversed(messages):
        if message.role == "user" and message.content.strip():
            return message.content.strip()
    return None


def _merge_results(
    primary: list[SearchResultItem],
    *extras: list[SearchResultItem],
    limit: int,
) -> list[SearchResultItem]:
    seen: set[str] = set()
    merged: list[SearchResultItem] = []
    for item in [*(chunk for extra in extras for chunk in extra), *primary]:
        if item.chunk_id in seen:
            continue
        seen.add(item.chunk_id)
        merged.append(item)
        if len(merged) >= limit:
            break
    return merged


def make_retriever_node(retrieval_service: RetrievalService | None = None):
    service = retrieval_service or RetrievalService()

    async def retriever_node(state: GraphState, config: RunnableConfig) -> dict:
        query = _last_user_message(state.messages)
        if not query:
            return {"retrieved_context": [], "errors": list(state.errors)}

        # INV-MTW-2: RAG reads only the active thesis corpus (project from
        # LangGraph config, never GraphState — ADR-0014).
        # `config` must be a required RunnableConfig so LangGraph injects it;
        # Optional+default None silently drops project scope to thesis-agent.
        configurable = config.get("configurable") or {}
        scope = SearchFilters(project_id=configurable.get("project_id"))

        try:
            limit = CORPUS_RETRIEVAL_LIMIT if is_corpus_list_query(query) else 10
            results, _model = await service.search(query, filters=scope, limit=limit)
            if is_corpus_list_query(query):
                exclusion_extra, _ = await service.search(
                    EXCLUSION_BOOST_QUERY, filters=scope, limit=4
                )
                corpus_extra, _ = await service.search(
                    CORPUS_LIST_BOOST_QUERY, filters=scope, limit=6
                )
                results = _merge_results(
                    results,
                    exclusion_extra,
                    corpus_extra,
                    limit=limit,
                )
        except EmbedFailedError:
            return {
                "retrieved_context": [],
                "errors": [
                    *state.errors,
                    AgentError(agent="retriever", message="embed_failed"),
                ],
            }

        if not results:
            return {
                "retrieved_context": [],
                "errors": [
                    *state.errors,
                    AgentError(agent="retriever", message="no_results"),
                ],
            }

        return {
            "retrieved_context": [
                RetrievedChunk(
                    chunk_id=r.chunk_id,
                    score=r.score,
                    content=r.content,
                    document_id=r.document_id,
                    document_title=r.document_title,
                    page_from=r.page_from,
                    page_to=r.page_to,
                )
                for r in results
            ],
            "errors": list(state.errors),
        }

    return retriever_node
