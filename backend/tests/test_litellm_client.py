import types
import pytest
from app.llm.litellm_client import LiteLLMClient


class _Delta:
    def __init__(self, content): self.content = content


class _Choice:
    def __init__(self, content, finish=None):
        self.delta = _Delta(content)
        self.finish_reason = finish


class _Chunk:
    def __init__(self, content, finish=None, usage=None):
        self.choices = [_Choice(content, finish)]
        self.usage = usage


async def _fake_acompletion(**kwargs):
    assert kwargs["stream"] is True
    assert kwargs["model"] == "vertex_ai/gemini-2.5-pro"

    async def gen():
        yield _Chunk("Hel")
        yield _Chunk("lo")
        yield _Chunk("", finish="stop", usage={"total_tokens": 5})
    return gen()


async def test_astream_yields_token_chunks(monkeypatch):
    import app.llm.litellm_client as mod
    monkeypatch.setattr(mod.litellm, "acompletion", _fake_acompletion)
    client = LiteLLMClient(project="p", location="europe-west1", model="gemini-2.5-pro")
    out = [c async for c in client.astream([{"role": "user", "content": "hi"}])]
    assert "".join(c.text for c in out) == "Hello"
    assert out[-1].finish_reason == "stop"
    assert out[-1].metadata.get("usage") == {"total_tokens": 5}
