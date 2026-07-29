from __future__ import annotations

from typing import Any

from app.runtime.action_loop.types import ActionLoopContext

_MAX_CHAPTER_EXCERPT_CHARS = 4000


def make_get_selection_context_tool(*, ctx: ActionLoopContext):
    def get_selection_context() -> dict[str, Any]:
        """Return the current selection and a truncated chapter excerpt."""
        return {
            "selection_text": ctx.selection_text,
            "chapter_excerpt": ctx.chapter_content[:_MAX_CHAPTER_EXCERPT_CHARS],
            "action": ctx.action,
        }

    return get_selection_context
