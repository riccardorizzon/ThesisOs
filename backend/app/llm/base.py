from typing import Protocol


class LLMClient(Protocol):
    async def generate(self, messages: list[dict], *, model: str | None = None, params: dict | None = None) -> str: ...
    async def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]: ...
    async def vision(self, messages: list[dict], *, model: str | None = None) -> str: ...


class NotConfiguredLLM:
    """M0 placeholder. Concrete Vertex/LiteLLM client lands in M1 (ADR-0002)."""

    async def generate(self, *a, **k):
        raise NotImplementedError("LLM wired in M1")

    async def embed(self, *a, **k):
        raise NotImplementedError("LLM wired in M1")

    async def vision(self, *a, **k):
        raise NotImplementedError("LLM wired in M1")
