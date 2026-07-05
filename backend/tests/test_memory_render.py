"""Tests for binding decisions in prompt render."""

from app.schemas.memory import PromptContext, PromptMemoryItem
from app.services.memory.render import render_prompt_context


def test_render_prompt_context_includes_binding_decisions_first():
    ctx = PromptContext(
        decisions=[
            PromptMemoryItem(
                id="d1",
                kind="decision",
                title="Project decisions",
                content="CORPUS-02 Barthes Mythologies escluso",
                version=1,
                pinned=False,
                key="decisions",
            )
        ],
        editable=[
            PromptMemoryItem(
                id="e1",
                kind="editable",
                title="Rules",
                content="Editable rules.",
                version=1,
                pinned=False,
            )
        ],
    )
    out = render_prompt_context(ctx)
    assert out.index("[BINDING DECISIONS]") < out.index("[EDITABLE MEMORY]")
    assert "CORPUS-02" in out
    assert "override contradictory" in out
