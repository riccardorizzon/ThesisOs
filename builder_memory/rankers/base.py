"""Ranking primitives and provenance records (ADR-0019)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from builder_memory.retriever.retriever import RetrievedChunk


@dataclass(frozen=True)
class RetrievalProvenance:
    """Structured provenance for Critic Agent and audit trails."""

    path: str
    score: float
    source_type: str

    def to_dict(self) -> dict[str, str | float]:
        return {
            "path": self.path,
            "score": round(self.score, 2),
            "source_type": self.source_type,
        }


class Ranker(Protocol):
    """Pluggable ranker — swap without changing Retriever (M3+)."""

    def rank(
        self,
        chunks: list[RetrievedChunk],
        *,
        agent_role: str,
    ) -> list[RetrievedChunk]: ...

    def provenance(
        self,
        chunks: list[RetrievedChunk],
        *,
        agent_role: str,
    ) -> list[RetrievalProvenance]: ...


def normalize_scores(raw_scores: list[float]) -> list[float]:
    """Min-max normalize to [0, 1]. Equal scores → 1.0."""
    if not raw_scores:
        return []
    lo, hi = min(raw_scores), max(raw_scores)
    if hi == lo:
        return [1.0] * len(raw_scores)
    return [(s - lo) / (hi - lo) for s in raw_scores]


def build_provenance(chunks: list[RetrievedChunk]) -> list[RetrievalProvenance]:
    """Build provenance from ranked chunks with normalized scores."""
    normed = normalize_scores([c.score for c in chunks])
    return [
        RetrievalProvenance(
            path=chunk.source_path,
            score=score,
            source_type=chunk.kind,
        )
        for chunk, score in zip(chunks, normed, strict=True)
    ]
