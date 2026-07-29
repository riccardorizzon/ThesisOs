from __future__ import annotations

from app.runtime.action_loop.tools.context import make_get_selection_context_tool
from app.runtime.action_loop.types import ActionLoopContext


def test_get_selection_context_returns_selection_and_chapter():
    ctx = ActionLoopContext(
        action="verify",
        project_id="p1",
        selection_text="Selected passage",
        chapter_content="Chapter body text",
        context_summary="Rules",
    )
    get_selection_context = make_get_selection_context_tool(ctx=ctx)

    result = get_selection_context()

    assert result["selection_text"] == "Selected passage"
    assert result["chapter_excerpt"] == "Chapter body text"
    assert result["action"] == "verify"


def test_get_selection_context_truncates_long_chapter():
    long_chapter = "x" * 5000
    ctx = ActionLoopContext(
        action="find-sources",
        project_id=None,
        selection_text=None,
        chapter_content=long_chapter,
        context_summary=None,
    )
    get_selection_context = make_get_selection_context_tool(ctx=ctx)

    result = get_selection_context()

    assert len(result["chapter_excerpt"]) == 4000
    assert result["chapter_excerpt"] == long_chapter[:4000]
