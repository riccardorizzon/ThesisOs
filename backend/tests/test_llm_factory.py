from app.llm.base import NotConfiguredLLM
from app.llm.litellm_client import LiteLLMClient
from app.llm.factory import get_llm_client


def test_factory_not_configured_without_project(monkeypatch):
    import app.llm.factory as mod
    monkeypatch.setattr(mod.settings, "google_cloud_project", "")
    assert isinstance(get_llm_client(), NotConfiguredLLM)


def test_factory_real_with_project(monkeypatch):
    import app.llm.factory as mod
    monkeypatch.setattr(mod.settings, "google_cloud_project", "thesisos-prod")
    monkeypatch.setattr(mod.settings, "vertex_location", "europe-west1")
    monkeypatch.setattr(mod.settings, "gemini_model", "gemini-2.5-pro")
    client = get_llm_client()
    assert isinstance(client, LiteLLMClient)
