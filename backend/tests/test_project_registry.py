"""Project registry tests — durable DB-backed SoR (ADR-0047)."""

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
