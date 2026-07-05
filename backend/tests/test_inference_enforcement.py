"""EWO-7C inference enforcement tests."""

from __future__ import annotations

import pytest

from app.graph.inference_enforcement import generate_with_citation_enforcement


class FakeLLM:
    def __init__(self, responses: list[str]):
        self._responses = list(responses)
        self.calls = 0

    async def astream(self, messages, *, model=None, params=None):
        text = self._responses[self.calls]
        self.calls += 1
        yield type("Chunk", (), {"text": text, "metadata": {}})()


@pytest.mark.asyncio
async def test_no_retry_when_author_date_present():
    llm = FakeLLM(["Secondo Albers (Albers, 1963) il colore è relazionale."])
    emitted: list[str] = []
    text, _, retried = await generate_with_citation_enforcement(
        llm,
        [{"role": "user", "content": "x"}],
        academic=True,
        emit=lambda ev: emitted.append(ev["text"]),
    )
    assert not retried
    assert llm.calls == 1
    assert "(Albers, 1963)" in text
    assert emitted == [text]


@pytest.mark.asyncio
async def test_retry_when_numeric_without_author_date():
    llm = FakeLLM(
        [
            "Teoria cromatica [2] nel design.",
            "Secondo Josef Albers (Albers, 1963) il colore è relazionale.",
        ]
    )
    emitted: list[str] = []
    text, _, retried = await generate_with_citation_enforcement(
        llm,
        [{"role": "user", "content": "x"}],
        academic=True,
        emit=lambda ev: emitted.append(ev["text"]),
    )
    assert retried
    assert llm.calls == 2
    assert "(Albers, 1963)" in text
    assert emitted == [text]
    assert "[2]" not in text
