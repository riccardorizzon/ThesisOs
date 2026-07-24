from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models

DEMO_THESIS_ID = "demo-thesis"


@dataclass(frozen=True)
class DemoChapterSeed:
    id: str
    title: str
    order_index: int
    content_md: str


DEMO_CHAPTERS: tuple[DemoChapterSeed, ...] = (
    DemoChapterSeed(
        id="00000000-0000-4000-8000-000000000101",
        title="Introduzione",
        order_index=0,
        content_md="# Introduzione\n\nUna tesi dimostrativa parte da una domanda chiara e delimitata.",
    ),
    DemoChapterSeed(
        id="00000000-0000-4000-8000-000000000102",
        title="Quadro teorico",
        order_index=1,
        content_md="# Quadro teorico\n\nIl quadro teorico definisce concetti e relazioni utili all’analisi.",
    ),
    DemoChapterSeed(
        id="00000000-0000-4000-8000-000000000103",
        title="Metodologia",
        order_index=2,
        content_md="# Metodologia\n\nIl metodo rende espliciti corpus, criteri e limiti della ricerca.",
    ),
    DemoChapterSeed(
        id="00000000-0000-4000-8000-000000000104",
        title="Analisi",
        order_index=3,
        content_md="# Analisi\n\nL’analisi collega le evidenze raccolte alla domanda di ricerca.",
    ),
    DemoChapterSeed(
        id="00000000-0000-4000-8000-000000000105",
        title="Conclusioni",
        order_index=4,
        content_md="# Conclusioni\n\nLe conclusioni sintetizzano risultati, limiti e sviluppi futuri.",
    ),
)


async def ensure_demo_seed(session: AsyncSession) -> None:
    seed_ids = [seed.id for seed in DEMO_CHAPTERS]
    seed_id_set = set(seed_ids)

    # Drop any non-curated demo chapters so copy-demo never ships dogfood noise.
    stale_ids = [
        row_id
        for row_id in (
            (
                await session.execute(
                    select(models.Chapter.id).where(
                        models.Chapter.project_id == DEMO_THESIS_ID,
                        models.Chapter.id.not_in(seed_id_set),
                    )
                )
            )
            .scalars()
            .all()
        )
    ]
    if stale_ids:
        await session.execute(
            delete(models.Proposal).where(models.Proposal.chapter_id.in_(stale_ids))
        )
        await session.execute(
            delete(models.Citation).where(models.Citation.chapter_id.in_(stale_ids))
        )
        await session.execute(
            delete(models.Chapter).where(models.Chapter.id.in_(stale_ids))
        )
        await session.flush()

    existing = {
        row.id: row
        for row in (
            (
                await session.execute(
                    select(models.Chapter).where(models.Chapter.id.in_(seed_ids))
                )
            )
            .scalars()
            .all()
        )
    }

    for seed in DEMO_CHAPTERS:
        row = existing.get(seed.id)
        if row is not None and row.project_id != DEMO_THESIS_ID:
            raise RuntimeError(f"demo seed id belongs to another project: {seed.id}")
        if row is None:
            row = models.Chapter(
                id=seed.id,
                project_id=DEMO_THESIS_ID,
                parent_id=None,
                order_index=seed.order_index,
                title=seed.title,
                status="draft",
                content_md=seed.content_md,
                summary=None,
                word_count=len(seed.content_md.split()),
                version=1,
            )
            session.add(row)
            await session.flush()
            session.add(
                models.ChapterVersion(
                    chapter_id=seed.id,
                    version=1,
                    change_kind="WRITE",
                    title=seed.title,
                    status="draft",
                    content_md=seed.content_md,
                    summary=None,
                    word_count=len(seed.content_md.split()),
                )
            )
            continue

        row.parent_id = None
        row.order_index = seed.order_index
        row.title = seed.title
        row.status = "draft"
        row.content_md = seed.content_md
        row.summary = None
        row.word_count = len(seed.content_md.split())

    await session.flush()


async def reset_demo_seed(session: AsyncSession) -> None:
    chapter_ids = list(
        (
            await session.execute(
                select(models.Chapter.id).where(
                    models.Chapter.project_id == DEMO_THESIS_ID
                )
            )
        )
        .scalars()
        .all()
    )
    if chapter_ids:
        await session.execute(
            delete(models.Proposal).where(
                models.Proposal.chapter_id.in_(chapter_ids)
            )
        )
        await session.execute(
            delete(models.Citation).where(
                models.Citation.chapter_id.in_(chapter_ids)
            )
        )
        await session.execute(
            delete(models.Note).where(models.Note.project_id == DEMO_THESIS_ID)
        )
        await session.execute(
            delete(models.Chapter).where(
                models.Chapter.project_id == DEMO_THESIS_ID
            )
        )
        await session.flush()
    await ensure_demo_seed(session)
