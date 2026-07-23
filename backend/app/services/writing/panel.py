"""Writing panel retrieval grounding (M7 P-WRITING-GROUND)."""

from __future__ import annotations

from app.schemas.graph_state import RetrievedChunk
from app.schemas.retrieval import SearchFilters, SearchResultItem
from app.services.retrieval import EmbedFailedError, RetrievalService

WRITING_PANEL_RETRIEVAL_LIMIT = 10
_MAX_QUERY_CHARS = 4000


class WritingPanelRetrievalError(Exception):
    """Raised when corpus search fails for a writing panel action."""


def build_retrieval_query(
    *,
    action: str,
    selection_text: str | None,
    chapter_content: str,
) -> str | None:
    """Compose a hybrid-search query from panel inputs."""
    parts: list[str] = []
    if selection_text and selection_text.strip():
        parts.append(selection_text.strip())
    chapter = chapter_content.strip()
    if chapter and (action == "find-sources" or not parts):
        parts.append(chapter[:_MAX_QUERY_CHARS])
    query = " ".join(parts).strip()
    return query[:_MAX_QUERY_CHARS] if query else None


def search_results_to_chunks(results: list[SearchResultItem]) -> list[RetrievedChunk]:
    return [
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
    ]


async def fetch_panel_retrieved_context(
    *,
    action: str,
    selection_text: str | None,
    chapter_content: str,
    project_id: str | None = None,
    retrieval_service: RetrievalService | None = None,
) -> list[RetrievedChunk]:
    """Run corpus search for a writing panel action; empty when no query text."""
    query = build_retrieval_query(
        action=action,
        selection_text=selection_text,
        chapter_content=chapter_content,
    )
    if not query:
        return []

    service = retrieval_service or RetrievalService()
    try:
        results, _model = await service.search(
            query,
            filters=SearchFilters(project_id=project_id),
            limit=WRITING_PANEL_RETRIEVAL_LIMIT,
        )
    except EmbedFailedError as exc:
        raise WritingPanelRetrievalError(str(exc)) from exc
    return search_results_to_chunks(results)
