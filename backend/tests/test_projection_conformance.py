"""Projection Conformance tests (PX3-EWO-005, SoR §9)."""

from fastapi.testclient import TestClient

from app.main import app
from app.services.conformance.projection import build_px3_projection, repo_root

client = TestClient(app)


def test_conformance_projection_schema_v1():
    res = client.get("/projects/thesis-agent/conformance/projection")
    assert res.status_code == 200
    body = res.json()
    assert body["schema_version"] == 1
    assert body["program_id"] == "thesisos-product-v2"
    assert "derived_at" in body
    assert body["supervisor"]["state"] == "WAIT"
    assert "wave_b_projection" in body["waves"]
    assert "PX3-EWO-005" in body["jobs"]


def test_projection_rebuild_is_deterministic_except_timestamp():
    first = build_px3_projection().model_dump(mode="json")
    second = build_px3_projection().model_dump(mode="json")
    first.pop("derived_at")
    second.pop("derived_at")
    assert first == second


def test_projection_read_only_get_only():
    """INV-R-11 — projection endpoint is GET; no mutation routes registered."""
    post = client.post("/projects/thesis-agent/conformance/projection")
    assert post.status_code == 405


def test_get_concept_detail_for_explain_page():
    res = client.get("/projects/thesis-agent/knowledge/concepts/aura")
    assert res.status_code == 200
    body = res.json()
    assert body["type"] == "concept"
    assert body["slug"] == "aura"
    assert body["definition"] is not None
    assert len(body["definition"]) > 0


def test_get_concept_detail_not_found():
    res = client.get("/projects/thesis-agent/knowledge/concepts/missing")
    assert res.status_code == 404
    assert res.json()["code"] == "concept_not_found"


def test_projection_does_not_compute_ready_set():
    """INV-R-12 — observability surfaces must not compute scheduling independently."""
    body = client.get("/projects/thesis-agent/conformance/projection").json()
    assert "ready_set" not in body
    assert "ready_jobs" not in body
    assert "dispatch" not in body
    for wave in body.get("waves", {}).values():
        assert "ready_set" not in wave

