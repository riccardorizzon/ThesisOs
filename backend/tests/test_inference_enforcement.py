"""EWO-7C inference enforcement tests."""

from __future__ import annotations

import pytest

from app.graph.inference_enforcement import generate_with_citation_enforcement


class FakeLLM:
    def __init__(self, responses: list[str]):
        self._responses = list(responses)
        self.calls = 0
        self.stream_params: list[dict | None] = []

    async def astream(self, messages, *, model=None, params=None):
        self.stream_params.append(params)
        text = self._responses[self.calls]
        self.calls += 1
        yield type("Chunk", (), {"text": text, "metadata": {}})()


class ChunkedLLM:
    def __init__(self) -> None:
        self.yielded = 0
        self.stream_params: list[dict | None] = []

    async def astream(self, messages, *, model=None, params=None):
        self.stream_params.append(params)
        self.yielded = 1
        yield type("Chunk", (), {"text": "Primo ", "metadata": {}})()
        self.yielded = 2
        yield type("Chunk", (), {"text": "secondo.", "metadata": {}})()


@pytest.mark.asyncio
async def test_non_academic_response_streams_each_chunk_immediately():
    llm = ChunkedLLM()
    emitted: list[str] = []
    emission_checkpoints: list[int] = []

    def emit(event: dict) -> None:
        emitted.append(event["text"])
        emission_checkpoints.append(llm.yielded)

    text, _, retried = await generate_with_citation_enforcement(
        llm,
        [{"role": "user", "content": "Ciao"}],
        academic=False,
        emit=emit,
    )

    assert text == "Primo secondo."
    assert emitted == ["Primo ", "secondo."]
    assert emission_checkpoints == [1, 2]
    assert llm.stream_params == [{"reasoning_effort": "minimal"}]
    assert not retried


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
    assert llm.stream_params == [None]
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
