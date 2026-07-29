"""Unit tests for writing panel action loop orchestrator."""

from __future__ import annotations

import pytest

from app.runtime.action_loop.types import AssistantTurn, ToolCall
from app.schemas.retrieval import SearchResultItem
from app.services.retrieval import EmbedFailedError
from app.services.writing.action_loop_runner import run_writing_panel_with_loop
from app.services.writing.panel import WritingPanelRetrievalError


class FakeLLM:
    async def acompletion_with_tools(self, messages, *, tools, model=None, params=None):
        raise AssertionError("acompletion_with_tools should not run when complete is injected")


class FakeRetrievalService:
    def __init__(self, *, results=None, fail=False):
        self._results = results or []
        self._fail = fail
        self.last_query: str | None = None

    async def search(self, query, *, filters=None, limit=10, hybrid_alpha=0.5, session=None):
        self.last_query = query
        if self._fail:
            raise EmbedFailedError("embedding unavailable")
        return self._results, "fake-model"


def _search_result() -> SearchResultItem:
    return SearchResultItem(
        chunk_id="c1",
        document_id="d1",
        chunk_hash="h1",
        score=0.9,
        content="Craft is the disciplined pursuit of quality.",
        document_title="The Craftsman",
        page_from=10,
    )


@pytest.mark.asyncio
async def test_run_panel_with_loop_accumulates_chunks_before_draft(monkeypatch):
    search_count = {"n": 0}

    async def fake_complete(messages, tools):
        search_count["n"] += 1
        if search_count["n"] < 3:
            return AssistantTurn(
                content=None,
                tool_calls=[
                    ToolCall(
                        id=str(search_count["n"]),
                        name="search_corpus",
                        arguments={"query": f"q{search_count['n']}"},
                    )
                ],
                finish_reason="tool_calls",
            )
        return AssistantTurn(content=None, tool_calls=[], finish_reason="stop")

    service = FakeRetrievalService(results=[_search_result()])

    async def fake_generate(llm, wire, *, academic, emit=None):
        if emit:
            emit({"type": "token", "text": "Draft text."})
        return "Draft text.", {}, False

    monkeypatch.setattr(
        "app.services.writing.action_loop_runner.generate_with_citation_enforcement",
        fake_generate,
    )

    result = await run_writing_panel_with_loop(
        llm=FakeLLM(),
        action="verify",
        project_id="p1",
        selection_text="sel",
        chapter_content="chapter",
        context_summary="rules",
        complete=fake_complete,
        retrieval_service=service,
    )

    assert search_count["n"] >= 2
    assert result.draft == "Draft text."
    assert result.metadata.get("loop_action") is True
    assert result.metadata.get("search_count") >= 2
    assert result.metadata.get("chunk_count") >= 1
    assert len(result.citations) == 1


@pytest.mark.asyncio
async def test_run_panel_with_loop_surfaces_embed_failure():
    search_count = {"n": 0}

    async def fake_complete(messages, tools):
        search_count["n"] += 1
        return AssistantTurn(
            content=None,
            tool_calls=[ToolCall(id="1", name="search_corpus", arguments={"query": "q1"})],
            finish_reason="tool_calls",
        )

    service = FakeRetrievalService(fail=True)

    with pytest.raises(WritingPanelRetrievalError, match="embedding unavailable"):
        await run_writing_panel_with_loop(
            llm=FakeLLM(),
            action="find-sources",
            project_id=None,
            selection_text="sel",
            chapter_content="chapter",
            context_summary=None,
            complete=fake_complete,
            retrieval_service=service,
        )
