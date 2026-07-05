"""Wave B integration navigation tests (PX3-EWO-007)."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_explorer_to_explain_api_chain():
    """Explorer list → Explain header/definition endpoints (Integration B wiring)."""
    listing = client.get(
        "/projects/thesis-agent/knowledge/objects",
        params={"type": "concept"},
    )
    assert listing.status_code == 200
    concepts = listing.json()["objects"]
    assert len(concepts) >= 1
    slug = concepts[0]["slug"]

    header = client.get(f"/projects/thesis-agent/knowledge/concepts/{slug}/header")
    assert header.status_code == 200
    assert header.json()["slug"] == slug

    definition = client.get(
        f"/projects/thesis-agent/knowledge/concepts/{slug}/definition"
    )
    assert definition.status_code == 200
    assert definition.json()["slug"] == slug


def test_projection_consumer_does_not_mutate_state():
    """INV-R-12 — repeated projection reads are idempotent (read-only consumer)."""
    first = client.get("/projects/thesis-agent/conformance/projection").json()
    second = client.get("/projects/thesis-agent/conformance/projection").json()
    first.pop("derived_at")
    second.pop("derived_at")
    assert first == second
