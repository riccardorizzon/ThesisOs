from app.core.config import settings
from app.llm.base import NotConfiguredLLM
from app.llm.litellm_client import LiteLLMClient


def _get_client(model: str):
    if settings.google_cloud_project:
        return LiteLLMClient(
            project=settings.google_cloud_project,
            location=settings.vertex_location,
            model=model,
        )
    return NotConfiguredLLM()


def get_llm_client():
    """Real Vertex client when configured (ADC + project), else the not-configured stub (ADR-0013)."""
    return _get_client(settings.gemini_model)


def get_orchestration_llm_client():
    return _get_client(settings.gemini_orchestration_model)
