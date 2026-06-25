"""Retriever LangGraph node — populates GraphState.retrieved_context (M4)."""

from __future__ import annotations

from app.schemas.graph_state import AgentError, GraphState, Message, RetrievedChunk
from app.services.retrieval import EmbedFailedError, RetrievalService


def _last_user_message(messages: list[Message]) -> str | None:
    for message in reversed(messages):
        if message.role == "user" and message.content.strip():
            return message.content.strip()
    return None


def make_retriever_node(retrieval_service: RetrievalService | None = None):
    service = retrieval_service or RetrievalService()

    async def retriever_node(state: GraphState) -> dict:
        query = _last_user_message(state.messages)
        if not query:
            return {"retrieved_context": [], "errors": list(state.errors)}

        try:
            results, _model = await service.search(query, limit=10)
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
                RetrievedChunk(chunk_id=r.chunk_id, score=r.score, content=r.content)
                for r in results
            ],
            "errors": list(state.errors),
        }

    return retriever_node
