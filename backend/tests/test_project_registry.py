"""Project registry tests — durable DB-backed SoR (ADR-0047)."""

import pytest
from sqlalchemy import select, text

from app.db import models
from app.services.project_registry import (
    ProjectCreateRequest,
    ProjectRegistryService,
    ProjectUpdateRequest,
)


async def test_list_includes_default_projects(db_session):
    svc = ProjectRegistryService()
    items = (await svc.list_projects()).items
    ids = {p.id for p in items}
    assert "thesis-agent" in ids
    assert "demo-thesis" in ids
    thesis = next(p for p in items if p.id == "thesis-agent")
    assert thesis.kind == "owned"
    assert thesis.display_name == (
        "Prima dei dieci minuti. Il processo creativo nel fashion design"
    )


async def test_create_project_sequential_ids(db_session):
    svc = ProjectRegistryService()
    first = await svc.create_project(ProjectCreateRequest(display_name="Nuova tesi"))
    second = await svc.create_project(ProjectCreateRequest(display_name="Altra tesi"))
    assert first.id == "thesis-002"
    assert second.id == "thesis-003"
    assert first.display_name == "Nuova tesi"
    assert first.kind == "owned"


async def test_created_project_survives_new_service_instance(db_session):
    entry = await ProjectRegistryService().create_project(
        ProjectCreateRequest(display_name="Persistente")
    )
    # New instance = no shared process state; only the DB row can answer.
    assert await ProjectRegistryService().has(entry.id)


async def test_has_demo_and_created(db_session):
    svc = ProjectRegistryService()
    assert await svc.has("demo-thesis")
    assert await svc.has("thesis-agent")
    assert not await svc.has("missing-project")
    entry = await svc.create_project(ProjectCreateRequest(display_name="Isolated"))
    assert await svc.has(entry.id)


async def test_rename_project(db_session):
    svc = ProjectRegistryService()
    entry = await svc.create_project(ProjectCreateRequest(display_name="Bozza"))
    renamed = await svc.rename(entry.id, ProjectUpdateRequest(display_name="Titolo vero"))
    assert renamed is not None
    assert renamed.display_name == "Titolo vero"
    fetched = await svc.get(entry.id)
    assert fetched is not None and fetched.display_name == "Titolo vero"
    assert await svc.rename("missing-project", ProjectUpdateRequest(display_name="X")) is None


@pytest.mark.asyncio
@pytest.mark.parametrize("project_id", ["thesis-agent", "demo-thesis"])
async def test_delete_project_rejects_protected_projects(project_id):
    with pytest.raises(Exception, match="protected_project"):
        await ProjectRegistryService().delete_project(
            project_id,
            confirmation_project_id=project_id,
        )


@pytest.mark.asyncio
async def test_delete_project_requires_exact_confirmation(db_session):
    db_session.add(
        models.Project(
            id="thesis-delete-confirm",
            display_name="Da eliminare",
            kind="owned",
        )
    )
    await db_session.commit()

    with pytest.raises(Exception, match="confirmation"):
        await ProjectRegistryService().delete_project(
            "thesis-delete-confirm",
            confirmation_project_id="wrong-project",
        )
    assert await ProjectRegistryService().has("thesis-delete-confirm")


@pytest.mark.asyncio
async def test_delete_project_removes_scoped_aggregates_only(db_session):
    project_id = "thesis-delete-fixture"
    db_session.add(
        models.Project(
            id=project_id,
            display_name="Fixture eliminabile",
            kind="owned",
        )
    )
    chapter = models.Chapter(project_id=project_id, title="Capitolo QA")
    document = models.Document(
        project_id=project_id,
        title="Documento QA",
        source_type="text",
        status="uploaded",
    )
    conversation = models.Conversation(project_id=project_id, title="Chat QA")
    memory = models.Memory(project_id=project_id, kind="user", content="Memoria QA")
    task = models.Task(project_id=project_id, title="Task QA")
    event = models.Event(project_id=project_id, type="QAEvent")
    db_session.add_all([chapter, document, conversation, memory, task, event])
    await db_session.flush()

    chunk = models.Chunk(
        document_id=document.id,
        chunk_index=0,
        chunk_hash="qa-delete-chunk",
        content="Contenuto QA",
    )
    source = models.Source(
        project_id=project_id,
        document_id=document.id,
        type="upload",
        slug="qa-delete-source",
        title="Fonte QA",
    )
    message = models.Message(
        conversation_id=conversation.id,
        role="user",
        content="Messaggio QA",
    )
    run = models.AgentRun(
        project_id=project_id,
        conversation_id=conversation.id,
        status="done",
    )
    proposal = models.Proposal(
        project_id=project_id,
        chapter_id=chapter.id,
        original="Prima",
        proposed="Dopo",
        action="rewrite",
    )
    note = models.Note(
        project_id=project_id,
        chapter_id=chapter.id,
        document_id=document.id,
        kind="note",
        content="Nota QA",
    )
    memory_version = models.MemoryVersion(
        memory_id=memory.id,
        version=1,
        content=memory.content,
        source="user",
    )
    db_session.add_all(
        [chunk, source, message, run, proposal, note, memory_version]
    )
    await db_session.flush()
    step = models.AgentStep(agent_run_id=run.id, status="done")
    citation = models.Citation(
        source_id=source.id,
        chapter_id=chapter.id,
    )
    db_session.add_all([step, citation])
    await db_session.commit()

    deleted = await ProjectRegistryService().delete_project(
        project_id,
        confirmation_project_id=project_id,
    )

    assert deleted is True
    assert await ProjectRegistryService().has(project_id) is False
    for model, row_id in [
        (models.Chapter, chapter.id),
        (models.Document, document.id),
        (models.Chunk, chunk.id),
        (models.Source, source.id),
        (models.Conversation, conversation.id),
        (models.Message, message.id),
        (models.AgentRun, run.id),
        (models.AgentStep, step.id),
        (models.Memory, memory.id),
        (models.MemoryVersion, memory_version.id),
        (models.Proposal, proposal.id),
        (models.Note, note.id),
        (models.Citation, citation.id),
        (models.Task, task.id),
        (models.Event, event.id),
    ]:
        assert await db_session.scalar(
            select(model.id).where(model.id == row_id)
        ) is None


@pytest.mark.asyncio
async def test_delete_unknown_project_returns_false():
    assert (
        await ProjectRegistryService().delete_project(
            "missing-project",
            confirmation_project_id="missing-project",
        )
        is False
    )


@pytest.mark.asyncio
async def test_delete_project_rolls_back_all_changes_on_failure(
    db_session,
    monkeypatch,
):
    import app.services.project_registry as project_registry_module

    project_id = "thesis-delete-rollback"
    db_session.add(
        models.Project(
            id=project_id,
            display_name="Rollback",
            kind="owned",
        )
    )
    event = models.Event(project_id=project_id, type="KeepMe")
    db_session.add(event)
    await db_session.commit()

    async def fail_after_first_delete(session, target_project_id):
        await session.execute(
            text("DELETE FROM events WHERE project_id = :pid"),
            {"pid": target_project_id},
        )
        raise RuntimeError("injected deletion failure")

    monkeypatch.setattr(
        project_registry_module,
        "_delete_project_rows",
        fail_after_first_delete,
    )

    with pytest.raises(RuntimeError, match="injected deletion failure"):
        await ProjectRegistryService().delete_project(
            project_id,
            confirmation_project_id=project_id,
        )

    assert await ProjectRegistryService().has(project_id)
    assert await db_session.scalar(
        select(models.Event.id).where(models.Event.id == event.id)
    ) == event.id
