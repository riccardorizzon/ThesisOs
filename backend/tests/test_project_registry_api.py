from fastapi.testclient import TestClient

from app.main import app
from app.services.project_registry import (
    ProjectConfirmationError,
    ProtectedProjectError,
)


class FakeProjectRegistry:
    async def delete_project(
        self,
        project_id: str,
        *,
        confirmation_project_id: str,
    ) -> bool:
        if project_id in {"thesis-agent", "demo-thesis"}:
            raise ProtectedProjectError(project_id)
        if confirmation_project_id != project_id:
            raise ProjectConfirmationError(project_id)
        return project_id != "missing-project"


def test_delete_project_204(monkeypatch):
    import app.api.project_registry as project_registry_api

    monkeypatch.setattr(project_registry_api, "_service", FakeProjectRegistry())
    response = TestClient(app).request(
        "DELETE",
        "/projects/thesis-002",
        json={"confirmation_project_id": "thesis-002"},
    )
    assert response.status_code == 204


def test_delete_project_protected_403(monkeypatch):
    import app.api.project_registry as project_registry_api

    monkeypatch.setattr(project_registry_api, "_service", FakeProjectRegistry())
    response = TestClient(app).request(
        "DELETE",
        "/projects/thesis-agent",
        json={"confirmation_project_id": "thesis-agent"},
    )
    assert response.status_code == 403
    assert response.json()["code"] == "protected_project"


def test_delete_project_confirmation_mismatch_422(monkeypatch):
    import app.api.project_registry as project_registry_api

    monkeypatch.setattr(project_registry_api, "_service", FakeProjectRegistry())
    response = TestClient(app).request(
        "DELETE",
        "/projects/thesis-002",
        json={"confirmation_project_id": "wrong"},
    )
    assert response.status_code == 422
    assert response.json()["code"] == "project_confirmation_mismatch"


def test_delete_project_missing_404(monkeypatch):
    import app.api.project_registry as project_registry_api

    monkeypatch.setattr(project_registry_api, "_service", FakeProjectRegistry())
    response = TestClient(app).request(
        "DELETE",
        "/projects/missing-project",
        json={"confirmation_project_id": "missing-project"},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "project_not_found"
