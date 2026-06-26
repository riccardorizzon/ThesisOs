"""Embedding reliability regression tests (M4 recovery, bug-4).

Pure tests for batch planning + retry/permanent-error handling — no DB/Vertex.
"""

from __future__ import annotations

import asyncio

import pytest

from app.services.retrieval.exceptions import EmbedFailedError
from app.services.retrieval.service import RetrievalService, plan_embedding_batches


def test_plan_batches_splits_by_token_budget():
    # ~4000 chars => ~1000 estimated tokens each; cap 2500 => 2 per batch.
    texts = ["a" * 4000] * 5
    batches = plan_embedding_batches(texts, max_tokens=2500, max_count=100)
    assert [len(b) for b in batches] == [2, 2, 1]
    assert [i for b in batches for i in b] == [0, 1, 2, 3, 4]


def test_plan_batches_splits_by_count():
    batches = plan_embedding_batches(["x"] * 5, max_tokens=10**9, max_count=2)
    assert [len(b) for b in batches] == [2, 2, 1]


def test_plan_batches_single_batch_when_small():
    assert plan_embedding_batches(["a", "b"], max_tokens=10**6, max_count=100) == [[0, 1]]


def test_plan_batches_empty():
    assert plan_embedding_batches([]) == []


def test_plan_batches_respects_default_budget():
    """Default caps: 14k tokens and 250 instances per batch."""
    # 1000 tokens each (4000 chars); 15 chunks => 2 batches under 14k cap.
    texts = ["a" * 4000] * 15
    batches = plan_embedding_batches(texts)
    assert len(batches) == 2
    assert len(batches[0]) == 14
    assert batches[1] == [14]
    for batch in batches:
        total = sum(len(texts[i]) // 4 for i in batch)
        assert total <= 14000
        assert len(batch) <= 250


class FlakyLLM:
    def __init__(self, fail_times=0, error=None):
        self.calls = 0
        self.fail_times = fail_times
        self.error = error or Exception("503 transient")

    async def embed(self, texts, *, model=None):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise self.error
        return [[0.0] * 768 for _ in texts]


async def _noop_sleep(*_a, **_k):
    return None


async def test_embed_retries_transient_then_succeeds(monkeypatch):
    monkeypatch.setattr(asyncio, "sleep", _noop_sleep)
    svc = RetrievalService(llm=FlakyLLM(fail_times=2))
    out = await svc._embed_with_retry(["x"])
    assert len(out) == 1
    assert svc._llm.calls == 3


async def test_embed_permanent_error_not_retried():
    svc = RetrievalService(llm=FlakyLLM(fail_times=99, error=Exception("400 BadRequest: token limit")))
    with pytest.raises(EmbedFailedError):
        await svc._embed_with_retry(["x"])
    assert svc._llm.calls == 1


async def test_embed_exhausts_retries_then_raises(monkeypatch):
    monkeypatch.setattr(asyncio, "sleep", _noop_sleep)
    svc = RetrievalService(llm=FlakyLLM(fail_times=99))
    with pytest.raises(EmbedFailedError):
        await svc._embed_with_retry(["x"])
    assert svc._llm.calls == 3
