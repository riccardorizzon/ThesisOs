from __future__ import annotations

from typing import Any

from app.schemas.graph_state import RetrievedChunk
from app.schemas.retrieval import SearchFilters
from app.services.writing.panel import search_results_to_chunks

_MAX_SEARCH_LIMIT = 10


def _coerce_limit(limit: int | str, *, default: int = 10) -> int:
    """LLM tool args often serialize integers as strings — coerce before min()."""
    try:
        value = int(limit)
    except (TypeError, ValueError):
        return default
    return max(1, value)


def _append_deduped(accumulate: list[RetrievedChunk], chunks: list[RetrievedChunk]) -> None:
    seen = {chunk.chunk_id for chunk in accumulate}
    for chunk in chunks:
        if chunk.chunk_id not in seen:
            accumulate.append(chunk)
            seen.add(chunk.chunk_id)


def _chunk_summaries(chunks: list[RetrievedChunk]) -> list[dict[str, Any]]:
    return [
        {
            "chunk_id": chunk.chunk_id,
            "score": chunk.score,
            "content": chunk.content,
            "document_title": chunk.document_title,
            "page_from": chunk.page_from,
        }
        for chunk in chunks
    ]


def make_search_corpus_tool(
    *,
    retrieval_service: Any,
    project_id: str | None,
    accumulate: list[RetrievedChunk],
):
    async def search_corpus(query: str, limit: int = 10) -> dict[str, Any]:
        """Search the thesis corpus for relevant passages."""
        effective_limit = min(_coerce_limit(limit), _MAX_SEARCH_LIMIT)
        results, _model = await retrieval_service.search(
            query,
            filters=SearchFilters(project_id=project_id),
            limit=effective_limit,
        )
        chunks = search_results_to_chunks(results)
        _append_deduped(accumulate, chunks)
        return {"count": len(chunks), "chunks": _chunk_summaries(chunks)}

    return search_corpus
