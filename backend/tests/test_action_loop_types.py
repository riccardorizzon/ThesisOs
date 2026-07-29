from app.runtime.action_loop.types import ActionLoopContext, ToolCall, AssistantTurn


def test_action_loop_context_fields():
    ctx = ActionLoopContext(
        action="verify",
        project_id="p1",
        selection_text="sel",
        chapter_content="chapter",
        context_summary="rules",
    )
    assert ctx.action == "verify"
    assert ctx.project_id == "p1"


def test_assistant_turn_tool_calls_default_empty():
    turn = AssistantTurn(content="done", tool_calls=[], finish_reason="stop")
    assert turn.tool_calls == []
