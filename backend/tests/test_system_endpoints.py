from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_metrics():
    r = client.get("/metrics")
    assert r.status_code == 200

def test_jobs_contract_not_implemented():
    r = client.post("/jobs", json={"type": "noop"})
    assert r.status_code in (202, 501)
