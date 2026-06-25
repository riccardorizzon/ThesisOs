from collections.abc import AsyncIterator

import litellm

from app.core.config import settings
from app.llm.base import TokenChunk


class LiteLLMClient:
    """LiteLLM → Vertex AI (ADC). Provider stays hidden behind this seam (ADR-0002)."""

    def __init__(self, *, project: str, location: str, model: str):
        self._project = project
        self._location = location
        self._model = model

    def _vertex_model(self, model: str | None) -> str:
        return f"vertex_ai/{model or self._model}"

    def _kwargs(self, messages: list[dict], model: str | None, params: dict | None) -> dict:
        return {
            "model": self._vertex_model(model),
            "messages": messages,
            "vertex_project": self._project,
            "vertex_location": self._location,
            **(params or {}),
        }

    async def generate(self, messages: list[dict], *, model: str | None = None, params: dict | None = None) -> str:
        resp = await litellm.acompletion(stream=False, **self._kwargs(messages, model, params))
        return resp.choices[0].message.content or ""

    async def astream(self, messages: list[dict], *, model: str | None = None, params: dict | None = None) -> AsyncIterator[TokenChunk]:
        stream = await litellm.acompletion(stream=True, **self._kwargs(messages, model, params))
        async for chunk in stream:
            choice = chunk.choices[0]
            text = getattr(choice.delta, "content", None) or ""
            finish = getattr(choice, "finish_reason", None)
            meta: dict = {}
            usage = getattr(chunk, "usage", None)
            if usage is not None:
                meta["usage"] = dict(usage) if not isinstance(usage, dict) else usage
            if text or finish or meta:
                yield TokenChunk(text=text, finish_reason=finish, metadata=meta)

    async def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        if not texts:
            return []
        embed_model = model or settings.embedding_model
        try:
            resp = await litellm.aembedding(
                model=f"vertex_ai/{embed_model}",
                input=texts,
                vertex_project=self._project,
                vertex_location=self._location,
            )
        except Exception as exc:
            raise NotImplementedError(f"embed failed: {exc}") from exc
        data = getattr(resp, "data", None) or []
        return [item["embedding"] for item in data]

    async def vision(self, messages: list[dict], *, model: str | None = None) -> str:
        raise NotImplementedError("vision wired in a later milestone")
