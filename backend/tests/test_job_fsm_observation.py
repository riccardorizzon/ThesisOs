"""Job FSM Observation tests (PX3-EWO-009, SoR §5)."""

from fastapi.testclient import TestClient

from app.main import app
from app.services.conformance.job_fsm import build_job_fsm_observation

client = TestClient(app)


def test_job_fsm_observation_schema():
    res = client.get("/projects/thesis-agent/conformance/job-fsm")
    assert res.status_code == 200
    body = res.json()
    assert body["schema_version"] == 1
    assert body["read_only"] is True
    assert body["source"] == "conformance/projection"
    assert len(body["vocabulary_domains"]) == 3
    assert len(body["aggregate_to_job_fsm"]) == 6


def test_vocabulary_domains_distinguish_lifecycle_from_job_fsm():
    observation = build_job_fsm_observation()
    domains = {row.domain: row for row in observation.vocabulary_domains}
    assert "product_lifecycle" in domains
    assert "mb2_aggregate" in domains
    assert "mb2_job_fsm" in domains
    assert "candidate" in domains["product_lifecycle"].values
    assert "waiting" in domains["mb2_aggregate"].values


def test_projection_jobs_use_aggregate_status():
    observation = build_job_fsm_observation()
    assert len(observation.projection_jobs) >= 5
    for job in observation.projection_jobs:
        assert job.ewo_id.startswith("PX3-")
        assert job.aggregate_status in {
            "waiting",
            "ready",
            "running",
            "pass",
            "fail",
            "locked",
        }
        assert job.job_fsm_subset is not None


def test_aggregate_to_job_fsm_mapping_complete():
    observation = build_job_fsm_observation()
    aggregates = {row.aggregate_status for row in observation.aggregate_to_job_fsm}
    assert aggregates == {"waiting", "ready", "running", "pass", "fail", "locked"}


def test_job_fsm_read_only_no_mutation():
    """INV-R-11 — job FSM observation is GET-only."""
    post = client.post("/projects/thesis-agent/conformance/job-fsm")
    assert post.status_code == 405


def test_inv_r_11_note_present():
    body = client.get("/projects/thesis-agent/conformance/job-fsm").json()
    assert "INV-R-11" in body["inv_r_11_note"]
