"""PX6 project registry tests."""

from app.services.project_registry import ProjectCreateRequest, ProjectRegistryService


def test_list_includes_default_projects():
    svc = ProjectRegistryService()
    items = svc.list_projects().items
    ids = {p.id for p in items}
    assert "thesis-agent" in ids
    assert "demo-thesis" in ids


def test_create_project():
    svc = ProjectRegistryService()
    entry = svc.create_project(ProjectCreateRequest(display_name="Nuova tesi"))
    assert entry.id
    assert entry.display_name == "Nuova tesi"
    assert entry.kind == "owned"


def test_has_demo_and_created():
    svc = ProjectRegistryService()
    assert svc.has("demo-thesis")
    assert svc.has("thesis-agent")
    assert not svc.has("missing-project")
    entry = svc.create_project(ProjectCreateRequest(display_name="Isolated"))
    assert svc.has(entry.id)
