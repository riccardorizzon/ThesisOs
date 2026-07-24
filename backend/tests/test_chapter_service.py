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
    ChapterNotDeletableError,
    ChapterNotFoundError,
    ChapterService,
    ChapterServiceError,
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


@pytest.mark.asyncio
async def test_user_chapter_is_deletable_and_can_be_deleted(db_session):
    svc = ChapterService()
    rec = await svc.create(ChapterCreate(title="Introduzione"), session=db_session)
    await db_session.commit()

    loaded = await svc.get(rec.id, session=db_session)
    assert loaded.deletable is True

    await svc.delete(rec.id, session=db_session)
    await db_session.commit()

    with pytest.raises(ChapterNotFoundError):
        await svc.get(rec.id, session=db_session)


@pytest.mark.asyncio
async def test_demo_project_chapter_not_deletable(db_session):
    svc = ChapterService()
    rec = await svc.create(
        ChapterCreate(
            title="Capitolo dimostrativo",
            project_id="demo-thesis",
            content_md="seed",
        ),
        session=db_session,
    )
    await db_session.commit()

    assert (await svc.get(rec.id, session=db_session)).deletable is False

    with pytest.raises(ChapterNotDeletableError):
        await svc.delete(rec.id, session=db_session)


@pytest.mark.asyncio
async def test_migration_protection_uses_content_metadata_not_title(db_session):
    svc = ChapterService()
    user_named = await svc.create(
        ChapterCreate(title="[kimi-claw] Note personali", content_md="Testo utente"),
        session=db_session,
    )
    migrated = await svc.create(
        ChapterCreate(
            title="Capitolo migrato",
            content_md="<!-- migration_slug:chapter-1 -->\nTesto migrato",
        ),
        session=db_session,
    )
    await db_session.commit()

    assert (await svc.get(user_named.id, session=db_session)).deletable is True
    assert (await svc.get(migrated.id, session=db_session)).deletable is False


@pytest.mark.asyncio
async def test_chapter_with_children_not_deletable(db_session):
    svc = ChapterService()
    parent = await svc.create(ChapterCreate(title="Parent"), session=db_session)
    await db_session.commit()
    await svc.create(
        ChapterCreate(title="Child", parent_id=parent.id, order_index=0),
        session=db_session,
    )
    await db_session.commit()

    with pytest.raises(ChapterNotDeletableError):
        await svc.delete(parent.id, session=db_session)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "title",
    ["Prova", "Craftsmanship", "Reti neurali", "E2E export"],
)
async def test_owned_chapter_visibility_never_depends_on_title(db_session, title):
    svc = ChapterService()
    owned = await svc.create(
        ChapterCreate(title=title, project_id="thesis-002"),
        session=db_session,
    )
    await db_session.commit()

    owned_list = await svc.list(
        ChapterListFilters(project_id="thesis-002", scope="owned"),
        session=db_session,
    )

    by_id = {item.id: item for item in owned_list}
    assert owned.id in by_id
    loaded = by_id[owned.id]
    assert loaded.title == title
    assert loaded.deletable is True


@pytest.mark.asyncio
async def test_copy_demo_structure_uses_demo_project_and_is_idempotent(db_session):
    svc = ChapterService()

    result = await svc.copy_demo_structure(
        project_id="thesis-002",
        session=db_session,
    )
    await db_session.commit()

    assert [item.title for item in result.created] == [
        "Introduzione",
        "Quadro teorico",
        "Metodologia",
        "Analisi",
        "Conclusioni",
    ]
    assert all(item.project_id == "thesis-002" for item in result.created)
    assert all(item.content_md == "" for item in result.created)
    assert all(item.deletable is True for item in result.created)

    second = await svc.copy_demo_structure(
        project_id="thesis-002",
        session=db_session,
    )
    await db_session.commit()
    assert second.created == []
    assert second.skipped_titles == [
        "Introduzione",
        "Quadro teorico",
        "Metodologia",
        "Analisi",
        "Conclusioni",
    ]


@pytest.mark.asyncio
async def test_copy_demo_structure_rejects_demo_as_destination(db_session):
    with pytest.raises(ChapterServiceError):
        await ChapterService().copy_demo_structure(
            project_id="demo-thesis",
            session=db_session,
        )


@pytest.mark.asyncio
async def test_listing_demo_project_self_heals_curated_seed(db_session):
    items = await ChapterService().list(
        ChapterListFilters(project_id="demo-thesis", scope="demo"),
        session=db_session,
    )

    assert [item.title for item in items] == [
        "Introduzione",
        "Quadro teorico",
        "Metodologia",
        "Analisi",
        "Conclusioni",
    ]
    assert all(item.deletable is False for item in items)
