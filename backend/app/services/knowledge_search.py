"""Knowledge search — ranked retrieval across concept objects (PX-4 §search)."""

from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session_async import AsyncSessionLocal
from app.models.knowledge import Concept
from app.services.knowledge.repository import ConceptRepository


def _score_concept(query: str, title: str, summary: str | None, definition: str | None) -> float:
    q = query.lower()
    title_l = title.lower()
    if title_l == q:
        return 1.0
    if title_l.startswith(q):
        return 0.9
    if q in title_l:
        return 0.75
    blob = " ".join(filter(None, [summary, definition])).lower()
    if q in blob:
        return 0.5
    return 0.0


async def search_concepts(
    project_id: str,
    query: str,
    *,
    limit: int = 20,
    session: AsyncSession | None = None,
) -> list[dict]:
    """Return concept envelopes with relevance score, highest first."""
    q = query.strip()
    if not q:
        return []

    async def _run(s: AsyncSession) -> list[dict]:
        repo = ConceptRepository()
        pattern = f"%{q}%"
        result = await s.execute(
            select(Concept)
            .where(
                Concept.project_id == project_id,
                or_(
                    Concept.title.ilike(pattern),
                    Concept.summary.ilike(pattern),
                    Concept.definition.ilike(pattern),
                    Concept.slug.ilike(pattern),
                ),
            )
            .order_by(func.length(Concept.title))
            .limit(limit * 2)
        )
        rows = result.scalars().all()
        scored: list[tuple[float, dict]] = []
        for row in rows:
            score = _score_concept(q, row.title, row.summary, row.definition)
            if score <= 0:
                continue
            envelope = await repo.get_by_slug(s, project_id, row.slug)
            scored.append((score, {**envelope.model_dump(), "score": score}))
        scored.sort(key=lambda x: (-x[0], x[1]["title"]))
        return [item for _, item in scored[:limit]]

    if session is not None:
        return await _run(session)
    async with AsyncSessionLocal() as s:
        return await _run(s)
