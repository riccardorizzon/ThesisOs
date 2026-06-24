from collections.abc import AsyncIterator
from typing import Protocol

from pydantic import BaseModel, Field


class TokenChunk(BaseModel):
    """Frozen streaming unit (ADR-0011): exactly these three fields."""
    text: str
    finish_reason: str | None = None
    metadata: dict = Field(default_factory=dict)


class LLMClient(Protocol):
    async def generate(self, messages: list[dict], *, model: str | None = None, params: dict | None = None) -> str: ...
    async def astream(self, messages: list[dict], *, model: str | None = None, params: dict | None = None) -> AsyncIterator[TokenChunk]: ...
    async def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]: ...
    async def vision(self, messages: list[dict], *, model: str | None = None) -> str: ...


class NotConfiguredLLM:
    """M0 placeholder. Real Vertex/LiteLLM client lands in M1 (ADR-0002)."""

    async def generate(self, *a, **k) -> str:
        raise NotImplementedError("LLM wired in M1")

    async def astream(self, *a, **k):
        raise NotImplementedError("LLM wired in M1")
        yield  # pragma: no cover  (makes this an async generator)

    async def embed(self, *a, **k):
        raise NotImplementedError("LLM wired in M1")

    async def vision(self, *a, **k):
        raise NotImplementedError("LLM wired in M1")
