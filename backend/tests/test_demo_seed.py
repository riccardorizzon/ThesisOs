from __future__ import annotations

import pytest
from sqlalchemy import select

from app.db import models
from app.schemas.chapter import ChapterCreate
from app.services.chapter import ChapterService
from app.services.demo_seed import (
    DEMO_CHAPTERS,
    DEMO_THESIS_ID,
    ensure_demo_seed,
    reset_demo_seed,
)


@pytest.mark.asyncio
async def test_ensure_demo_seed_is_curated_and_idempotent(db_session):
    await ensure_demo_seed(db_session)
    await ensure_demo_seed(db_session)
    await db_session.commit()

    rows = (
        (
            await db_session.execute(
                select(models.Chapter)
                .where(models.Chapter.project_id == DEMO_THESIS_ID)
                .order_by(models.Chapter.order_index)
            )
        )
        .scalars()
        .all()
    )

    assert [row.id for row in rows] == [seed.id for seed in DEMO_CHAPTERS]
    assert [row.title for row in rows] == [
        "Introduzione",
        "Quadro teorico",
        "Metodologia",
        "Analisi",
        "Conclusioni",
    ]
    assert all(row.content_md and "dogfood" not in row.content_md.lower() for row in rows)


@pytest.mark.asyncio
async def test_reset_demo_seed_never_touches_owned_chapters(db_session):
    service = ChapterService()
    owned = await service.create(
        ChapterCreate(project_id="thesis-002", title="Capitolo reale"),
        session=db_session,
    )
    dirty = await service.create(
        ChapterCreate(project_id=DEMO_THESIS_ID, title="E2E export"),
        session=db_session,
    )
    await db_session.commit()

    await reset_demo_seed(db_session)
    await db_session.commit()

    assert (await service.get(owned.id, session=db_session)).title == "Capitolo reale"
    demo_rows = (
        (
            await db_session.execute(
                select(models.Chapter)
                .where(models.Chapter.project_id == DEMO_THESIS_ID)
                .order_by(models.Chapter.order_index)
            )
        )
        .scalars()
        .all()
    )
    assert dirty.id not in {row.id for row in demo_rows}
    assert [row.id for row in demo_rows] == [seed.id for seed in DEMO_CHAPTERS]
