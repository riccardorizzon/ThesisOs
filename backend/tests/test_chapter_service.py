"""ChapterService unit tests (M6.3, ADR-0032/0033)."""

from __future__ import annotations

import pytest
from sqlalchemy import select

from app.db import models
from app.schemas.chapter import (
    ChapterContentUpdate,
    ChapterCreate,
    ChapterListFilters,
    ChapterMetadataUpdate,
)
from app.services.chapter import (
    ChapterNotFoundError,
    ChapterService,
    ChapterWriteConflictError,
    InvalidChapterStatusError,
)


async def _versions(session, chapter_id):
    rows = (
        await session.execute(
            select(models.ChapterVersion)
            .where(models.ChapterVersion.chapter_id == chapter_id)
            .order_by(models.ChapterVersion.version)
        )
    ).scalars().all()
    return rows


@pytest.mark.asyncio
async def test_create_starts_at_version_1_with_write_change(db_session):
    svc = ChapterService()
    rec = await svc.create(
        ChapterCreate(title="Introduction", content_md="Hello world draft."),
        session=db_session,
    )
    await db_session.commit()

    assert rec.version == 1
    assert rec.status == "draft"
    assert rec.word_count == 3
    versions = await _versions(db_session, rec.id)
    assert [(v.version, v.change_kind) for v in versions] == [(1, "WRITE")]


@pytest.mark.asyncio
async def test_update_content_increments_version_and_appends_edit(db_session):
    svc = ChapterService()
    rec = await svc.create(ChapterCreate(title="Ch", content_md="one"), session=db_session)
    await db_session.commit()

    updated = await svc.update_content(
        rec.id, ChapterContentUpdate(content_md="one two three", expected_version=1), session=db_session
    )
    await db_session.commit()

    assert updated.version == 2
    assert updated.word_count == 3
    versions = await _versions(db_session, rec.id)
    assert [(v.version, v.change_kind) for v in versions] == [(1, "WRITE"), (2, "EDIT")]


@pytest.mark.asyncio
async def test_status_transition_records_promote(db_session):
    svc = ChapterService()
    rec = await svc.create(ChapterCreate(title="Ch", content_md="x"), session=db_session)
    await db_session.commit()

    promoted = await svc.update_metadata(
        rec.id, ChapterMetadataUpdate(status="review", expected_version=1), session=db_session
    )
    await db_session.commit()

    assert promoted.status == "review"
    versions = await _versions(db_session, rec.id)
    assert versions[-1].change_kind == "PROMOTE"


@pytest.mark.asyncio
async def test_metadata_edit_without_status_records_edit(db_session):
    svc = ChapterService()
    rec = await svc.create(ChapterCreate(title="Old", content_md="x"), session=db_session)
    await db_session.commit()

    out = await svc.update_metadata(
        rec.id, ChapterMetadataUpdate(title="New", summary="s", expected_version=1), session=db_session
    )
    await db_session.commit()

    assert out.title == "New"
    assert out.summary == "s"
    versions = await _versions(db_session, rec.id)
    assert versions[-1].change_kind == "EDIT"


@pytest.mark.asyncio
async def test_optimistic_lock_conflict(db_session):
    svc = ChapterService()
    rec = await svc.create(ChapterCreate(title="Ch", content_md="x"), session=db_session)
    await db_session.commit()

    with pytest.raises(ChapterWriteConflictError):
        await svc.update_content(
            rec.id, ChapterContentUpdate(content_md="y", expected_version=99), session=db_session
        )


@pytest.mark.asyncio
async def test_reserved_lifecycle_states_accepted(db_session):
    """approved/published are reserved but valid values (no auto-transition)."""
    svc = ChapterService()
    rec = await svc.create(ChapterCreate(title="Ch", content_md="x"), session=db_session)
    await db_session.commit()
    v = 1
    for status in ("review", "approved", "published"):
        out = await svc.update_metadata(
            rec.id, ChapterMetadataUpdate(status=status, expected_version=v), session=db_session
        )
        await db_session.commit()
        v = out.version
        assert out.status == status


@pytest.mark.asyncio
async def test_invalid_status_rejected(db_session):
    svc = ChapterService()
    with pytest.raises(InvalidChapterStatusError):
        await svc.create(ChapterCreate(title="Ch", status="banana"), session=db_session)


@pytest.mark.asyncio
async def test_get_not_found(db_session):
    svc = ChapterService()
    with pytest.raises(ChapterNotFoundError):
        await svc.get("00000000-0000-0000-0000-000000000000", session=db_session)


@pytest.mark.asyncio
async def test_list_orders_by_order_index_and_filters_title(db_session):
    svc = ChapterService()
    await svc.create(ChapterCreate(title="Beta chapter", order_index=2), session=db_session)
    await svc.create(ChapterCreate(title="Alpha chapter", order_index=1), session=db_session)
    await svc.create(ChapterCreate(title="Gamma intro", order_index=3), session=db_session)
    await db_session.commit()

    ordered = await svc.list(session=db_session)
    assert [c.order_index for c in ordered] == [1, 2, 3]

    filtered = await svc.list(ChapterListFilters(q="chapter"), session=db_session)
    titles = {c.title for c in filtered}
    assert titles == {"Alpha chapter", "Beta chapter"}


@pytest.mark.asyncio
async def test_section_via_parent_id(db_session):
    svc = ChapterService()
    parent = await svc.create(ChapterCreate(title="Chapter 1"), session=db_session)
    await db_session.commit()
    child = await svc.create(
        ChapterCreate(title="Section 1.1", parent_id=parent.id, order_index=0), session=db_session
    )
    await db_session.commit()

    assert child.parent_id == parent.id
    children = await svc.list(ChapterListFilters(parent_id=parent.id), session=db_session)
    assert [c.id for c in children] == [child.id]


@pytest.mark.asyncio
async def test_list_versions_returns_ordered_change_stream(db_session):
    svc = ChapterService()
    rec = await svc.create(ChapterCreate(title="Ch", content_md="a"), session=db_session)
    await db_session.commit()
    await svc.update_content(
        rec.id, ChapterContentUpdate(content_md="a b", expected_version=1), session=db_session
    )
    await db_session.commit()

    history = await svc.list_versions(rec.id, session=db_session)
    assert [(v.version, v.change_kind) for v in history] == [(1, "WRITE"), (2, "EDIT")]
