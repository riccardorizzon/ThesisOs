from app.core.config import settings
from app.llm.base import NotConfiguredLLM
from app.llm.litellm_client import LiteLLMClient


def get_llm_client():
    """Real Vertex client when configured (ADC + project), else the not-configured stub (ADR-0013)."""
    if settings.google_cloud_project:
        return LiteLLMClient(
            project=settings.google_cloud_project,
            location=settings.vertex_location,
            model=settings.gemini_model,
        )
    return NotConfiguredLLM()
