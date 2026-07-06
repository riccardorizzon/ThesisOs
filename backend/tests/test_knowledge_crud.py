"""PX-4 concept CRUD API tests (requires migrated test DB)."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
PROJECT = "thesis-agent"


@pytest.mark.asyncio
async def test_create_concept(db_session):
    res = client.post(
        f"/projects/{PROJECT}/knowledge/concepts",
        json={
            "slug": "test-concept",
            "title": "Test Concept",
            "summary": "A test definition.",
            "source_slugs": ["benjamin-opera-arte"],
        },
    )
    assert res.status_code == 201
    body = res.json()
    assert body["slug"] == "test-concept"
    assert body["type"] == "concept"
    assert body["knowledge_state"] == "validated"
    assert body["linked_counts"]["sources"] == 1


@pytest.mark.asyncio
async def test_create_concept_duplicate_slug(db_session):
    payload = {"slug": "dup-concept", "title": "First"}
    assert client.post(f"/projects/{PROJECT}/knowledge/concepts", json=payload).status_code == 201
    res = client.post(f"/projects/{PROJECT}/knowledge/concepts", json=payload)
    assert res.status_code == 409
    assert res.json()["code"] == "concept_slug_exists"


@pytest.mark.asyncio
async def test_update_concept(db_session):
    client.post(
        f"/projects/{PROJECT}/knowledge/concepts",
        json={"slug": "patch-me", "title": "Before"},
    )
    res = client.patch(
        f"/projects/{PROJECT}/knowledge/concepts/patch-me",
        json={"title": "After", "knowledge_state": "validated"},
    )
    assert res.status_code == 200
    assert res.json()["title"] == "After"


@pytest.mark.asyncio
async def test_delete_concept(db_session):
    client.post(
        f"/projects/{PROJECT}/knowledge/concepts",
        json={"slug": "delete-me", "title": "Gone"},
    )
    res = client.delete(f"/projects/{PROJECT}/knowledge/concepts/delete-me")
    assert res.status_code == 204
    get_res = client.get(f"/projects/{PROJECT}/knowledge/objects/delete-me")
    assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_list_uses_db_after_seed(db_session):
    """After migration seed, concepts come from DB (7 seeded + any created in test)."""
    res = client.get(f"/projects/{PROJECT}/knowledge/objects", params={"type": "concept"})
    assert res.status_code == 200
    body = res.json()
    assert body["total"] >= 7
    slugs = {o["slug"] for o in body["objects"]}
    assert "aura" in slugs
