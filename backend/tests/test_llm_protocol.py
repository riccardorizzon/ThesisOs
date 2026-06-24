import pytest
from app.llm.base import TokenChunk, NotConfiguredLLM


def test_tokenchunk_frozen_fields():
    c = TokenChunk(text="hi")
    assert c.text == "hi"
    assert c.finish_reason is None
    assert c.metadata == {}
    # exactly three fields — no accidental widening
    assert set(TokenChunk.model_fields) == {"text", "finish_reason", "metadata"}


async def test_not_configured_astream_raises():
    llm = NotConfiguredLLM()
    with pytest.raises(NotImplementedError):
        async for _ in llm.astream([{"role": "user", "content": "hi"}]):
            pass
