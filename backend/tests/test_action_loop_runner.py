import pytest
from pathlib import Path

from app.runtime.action_loop.loop import ActionLoopRunner
from app.runtime.action_loop.permissions import PermissionEngine
from app.runtime.action_loop.registry import ToolRegistry
from app.runtime.action_loop.tools import build_panel_tools
from app.runtime.action_loop.types import ActionLoopContext, AssistantTurn, ToolCall
from app.schemas.retrieval import SearchResultItem
from tests.test_action_loop_tools_corpus import FakeRetrievalService


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
async def test_loop_runs_tools_until_no_tool_calls():
    calls = {"n": 0}

    async def fake_complete(messages, tools):
        calls["n"] += 1
        if calls["n"] == 1:
            return AssistantTurn(
                content=None,
                tool_calls=[ToolCall(id="1", name="search_corpus", arguments={"query": "a"})],
                finish_reason="tool_calls",
            )
        return AssistantTurn(content="done", tool_calls=[], finish_reason="stop")

    reg = ToolRegistry()
    reg.register(lambda query: {"hits": 1}, name="search_corpus")

    runner = ActionLoopRunner(
        registry=reg,
        permissions=PermissionEngine(workspace_root=Path("/tmp")),
        complete=fake_complete,
        max_iterations=6,
    )
    result = await runner.run(messages=[{"role": "user", "content": "find sources"}])
    assert calls["n"] == 2
    assert result.steps


@pytest.mark.asyncio
async def test_loop_with_build_panel_tools_accumulates_chunks():
    calls = {"n": 0}
    accumulate = []
    ctx = ActionLoopContext(
        action="find-sources",
        project_id="p1",
        selection_text="craft",
        chapter_content="Chapter",
        context_summary=None,
    )
    service = FakeRetrievalService(results=[_search_result()])

    async def fake_complete(messages, tools):
        calls["n"] += 1
        if calls["n"] == 1:
            return AssistantTurn(
                content=None,
                tool_calls=[ToolCall(id="1", name="search_corpus", arguments={"query": "craft"})],
                finish_reason="tool_calls",
            )
        return AssistantTurn(content="done", tool_calls=[], finish_reason="stop")

    runner = ActionLoopRunner(
        registry=build_panel_tools(ctx, service, accumulate),
        permissions=PermissionEngine(workspace_root=Path("/tmp")),
        complete=fake_complete,
        max_iterations=6,
    )
    result = await runner.run(messages=[{"role": "user", "content": "find sources"}])

    assert calls["n"] == 2
    assert len(accumulate) == 1
    assert accumulate[0].chunk_id == "c1"
    assert result.tool_calls[0].name == "search_corpus"
