from __future__ import annotations

from app.runtime.action_loop.risk import classify
from app.runtime.action_loop.tools import build_panel_tools
from app.runtime.action_loop.types import ActionLoopContext
from tests.test_action_loop_tools_corpus import FakeRetrievalService


def test_build_panel_tools_registers_expected_names():
    ctx = ActionLoopContext(
        action="verify",
        project_id="p1",
        selection_text="sel",
        chapter_content="chapter",
        context_summary=None,
    )
    registry = build_panel_tools(ctx, FakeRetrievalService(), accumulate=[])

    names = {schema["function"]["name"] for schema in registry.schemas()}
    assert names == {"search_corpus", "get_selection_context"}
    assert classify("search_corpus").value == "read"
    assert classify("get_selection_context").value == "read"
