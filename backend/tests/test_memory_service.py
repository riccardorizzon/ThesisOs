import asyncio

import pytest
from sqlalchemy import text

from app.db import models
from app.db.session_async import AsyncSessionLocal
from app.schemas.memory import MemoryCreate, MemoryListFilters, MemoryUpdate, PromptContextFilters
from app.services.memory import MemoryService, WriteConflictError, prompt_context_kinds, render_prompt_context
from app.services.memory.exceptions import (
    CannotDeleteSingletonError,
    MemoryNotFoundError,
    SingletonMemoryExistsError,
)


@pytest.fixture
def memory_svc() -> MemoryService:
    return MemoryService()


async def test_crud_multi_kind(memory_svc: MemoryService, db_session):
    created = await memory_svc.create(
        MemoryCreate(kind="concept", title="Habitus", content="Bourdieu concept", key="habitus"),
        session=db_session,
    )
    assert created.kind == "concept"
    assert created.version == 1

    fetched = await memory_svc.get(created.id, session=db_session)
    assert fetched.content == "Bourdieu concept"

    updated = await memory_svc.update(
        created.id,
        MemoryUpdate(content="Updated definition", expected_version=1),
        session=db_session,
    )
    assert updated.version == 2
    assert updated.content == "Updated definition"

    rows = await memory_svc.list(MemoryListFilters(kind="concept", q="Habitus"), session=db_session)
    assert any(r.id == created.id for r in rows)

    await memory_svc.delete(created.id, session=db_session)
    with pytest.raises(MemoryNotFoundError):
        await memory_svc.get(created.id, session=db_session)


async def test_version_chain(memory_svc: MemoryService, db_session):
    m = await memory_svc.create(
        MemoryCreate(kind="decision", title="Method", content="v1 body"),
        session=db_session,
    )
    await memory_svc.update(
        m.id,
        MemoryUpdate(content="v2 body", expected_version=1),
        session=db_session,
    )
    await memory_svc.update(
        m.id,
        MemoryUpdate(content="v3 body", expected_version=2),
        session=db_session,
    )

    versions = await memory_svc.list_versions(m.id, session=db_session)
    assert [v.version for v in versions] == [1, 2, 3]
    assert [v.content for v in versions] == ["v1 body", "v2 body", "v3 body"]

    v2 = await memory_svc.get_version(m.id, 2, session=db_session)
    assert v2.content == "v2 body"


async def test_write_conflict_on_stale_version(memory_svc: MemoryService, db_session):
    m = await memory_svc.create(
        MemoryCreate(kind="concept", content="initial"),
        session=db_session,
    )
    await memory_svc.update(
        m.id,
        MemoryUpdate(content="v2", expected_version=1),
        session=db_session,
    )
    with pytest.raises(WriteConflictError) as exc:
        await memory_svc.update(
            m.id,
            MemoryUpdate(content="stale", expected_version=1),
            session=db_session,
        )
    assert exc.value.expected_version == 1
    assert exc.value.actual_version == 2


async def test_concurrent_update_conflict(memory_svc: MemoryService, db_session):
    m = await memory_svc.create(
        MemoryCreate(kind="concept", content="race"),
        session=db_session,
    )
    await db_session.commit()

    async def attempt(label: str):
        async with AsyncSessionLocal() as s:
            try:
                result = await memory_svc.update(
                    m.id,
                    MemoryUpdate(content=label, expected_version=1),
                    session=s,
                )
                await s.commit()
                return result
            except WriteConflictError:
                await s.rollback()
                raise

    results = await asyncio.gather(attempt("a"), attempt("b"), return_exceptions=True)
    successes = [r for r in results if not isinstance(r, Exception)]
    conflicts = [r for r in results if isinstance(r, WriteConflictError)]
    assert len(successes) == 1
    assert len(conflicts) == 1

    async with AsyncSessionLocal() as cleanup:
        row = await cleanup.get(models.Memory, m.id)
        if row is not None:
            await cleanup.delete(row)
            await cleanup.commit()


async def test_prompt_context_operational_only(memory_svc: MemoryService, db_session):
    await memory_svc.create(
        MemoryCreate(kind="editable", content="Always inject rules"),
        session=db_session,
    )
    await memory_svc.create(
        MemoryCreate(kind="user", content="Pinned prefs", pinned=True),
        session=db_session,
    )
    await memory_svc.create(
        MemoryCreate(kind="thesis", content="Pinned scope", pinned=True),
        session=db_session,
    )
    await memory_svc.create(
        MemoryCreate(kind="concept", content="Should not inject", title="Concept X"),
        session=db_session,
    )
    await memory_svc.create(
        MemoryCreate(kind="citation", content="Should not inject", title="Citation Y"),
        session=db_session,
    )
    await memory_svc.create(
        MemoryCreate(kind="decision", content="Should not inject", title="Decision Z"),
        session=db_session,
    )

    ctx = await memory_svc.load_prompt_context(
        conversation_id="conv-test",
        max_tokens=8000,
        filters=PromptContextFilters(),
        session=db_session,
    )

    kinds = prompt_context_kinds(ctx)
    assert kinds == {"editable", "user", "thesis"}
    assert ctx.conversation_id == "conv-test"
    assert len(ctx.editable) == 1
    assert "Always inject rules" in ctx.editable[0].content

    rendered = render_prompt_context(ctx)
    assert "[EDITABLE MEMORY]" in rendered
    assert "Concept X" not in rendered
    assert "Citation Y" not in rendered
    assert "Decision Z" not in rendered


async def test_prompt_context_excludes_unpinned_user_thesis(memory_svc: MemoryService, db_session):
    await memory_svc.create(
        MemoryCreate(kind="editable", content="Rules"),
        session=db_session,
    )
    await memory_svc.create(
        MemoryCreate(kind="user", content="Unpinned", pinned=False),
        session=db_session,
    )
    await memory_svc.create(
        MemoryCreate(kind="thesis", content="Unpinned thesis", pinned=False),
        session=db_session,
    )

    ctx = await memory_svc.load_prompt_context(session=db_session)
    assert len(ctx.editable) == 1
    assert ctx.user == []
    assert ctx.thesis == []


async def test_singleton_duplicate_rejected(memory_svc: MemoryService, db_session):
    await memory_svc.create(MemoryCreate(kind="editable", content="Page"), session=db_session)
    with pytest.raises(SingletonMemoryExistsError):
        await memory_svc.create(MemoryCreate(kind="editable", content="Again"), session=db_session)


async def test_cannot_delete_singleton(memory_svc: MemoryService, db_session):
    editable = await memory_svc.create(
        MemoryCreate(kind="editable", content="Page"),
        session=db_session,
    )
    with pytest.raises(CannotDeleteSingletonError):
        await memory_svc.delete(editable.id, session=db_session)
