from app.llm.base import NotConfiguredLLM
from app.llm.litellm_client import LiteLLMClient
from app.llm.factory import get_llm_client, get_orchestration_llm_client


def test_factory_not_configured_without_project(monkeypatch):
    import app.llm.factory as mod
    monkeypatch.setattr(mod.settings, "google_cloud_project", "")
    assert isinstance(get_llm_client(), NotConfiguredLLM)
    assert isinstance(get_orchestration_llm_client(), NotConfiguredLLM)


def test_factory_uses_tiered_models(monkeypatch):
    import app.llm.factory as mod

    monkeypatch.setattr(mod.settings, "google_cloud_project", "thesisos-prod")
    monkeypatch.setattr(mod.settings, "vertex_location", "global")
    monkeypatch.setattr(mod.settings, "gemini_model", "gemini-3.6-flash")
    monkeypatch.setattr(
        mod.settings,
        "gemini_orchestration_model",
        "gemini-3.5-flash-lite",
    )

    response = get_llm_client()
    orchestration = get_orchestration_llm_client()

    assert isinstance(response, LiteLLMClient)
    assert response._location == "global"
    assert response._model == "gemini-3.6-flash"
    assert isinstance(orchestration, LiteLLMClient)
    assert orchestration._location == "global"
    assert orchestration._model == "gemini-3.5-flash-lite"
