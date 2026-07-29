"""ADR-0048 optional shared beta token gate."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import settings
from app.middleware.beta_access import BetaAccessMiddleware


def _app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(BetaAccessMiddleware)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/chat")
    def chat():
        return {"ok": True}

    return app


def test_beta_token_disabled_allows_all(monkeypatch):
    monkeypatch.setattr(settings, "beta_access_token", "")
    client = TestClient(_app())
    assert client.get("/health").status_code == 200
    assert client.get("/chat").status_code == 200


def test_beta_token_required_when_configured(monkeypatch):
    monkeypatch.setattr(settings, "beta_access_token", "secret-demo")
    client = TestClient(_app())
    assert client.get("/health").status_code == 200
    denied = client.get("/chat")
    assert denied.status_code == 401
    assert denied.json()["code"] == "beta_token_required"
    ok = client.get("/chat", headers={"X-Beta-Token": "secret-demo"})
    assert ok.status_code == 200


def test_beta_token_rejects_wrong_value(monkeypatch):
    monkeypatch.setattr(settings, "beta_access_token", "secret-demo")
    client = TestClient(_app())
    assert client.get("/chat", headers={"X-Beta-Token": "nope"}).status_code == 401
