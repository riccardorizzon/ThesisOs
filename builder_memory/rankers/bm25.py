"""BM25 ranker with role-based kind weights (V1 default)."""

from __future__ import annotations

from builder_memory.config import ROLE_KIND_WEIGHTS
from builder_memory.rankers.base import RetrievalProvenance, build_provenance
from builder_memory.retriever.retriever import RetrievedChunk


class Bm25Ranker:
    """V1 ranker: raw BM25 scores + role kind multipliers + min-max normalization."""

    def rank(
        self,
        chunks: list[RetrievedChunk],
        *,
        agent_role: str,
    ) -> list[RetrievedChunk]:
        weights = ROLE_KIND_WEIGHTS.get(agent_role, {})
        weighted: list[RetrievedChunk] = []
        for chunk in chunks:
            weight = weights.get(chunk.kind, 1.0)
            weighted.append(
                RetrievedChunk(
                    content=chunk.content,
                    source_path=chunk.source_path,
                    kind=chunk.kind,
                    title=chunk.title,
                    heading_path=chunk.heading_path,
                    chunk_id=chunk.chunk_id,
                    score=chunk.score * weight,
                )
            )
        weighted.sort(key=lambda c: c.score, reverse=True)
        return weighted

    def provenance(
        self,
        chunks: list[RetrievedChunk],
        *,
        agent_role: str,
    ) -> list[RetrievalProvenance]:
        ranked = self.rank(chunks, agent_role=agent_role)
        return build_provenance(ranked)
