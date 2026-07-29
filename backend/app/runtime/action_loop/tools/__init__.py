from __future__ import annotations

from typing import Any

from app.runtime.action_loop.registry import ToolRegistry
from app.runtime.action_loop.tools.context import make_get_selection_context_tool
from app.runtime.action_loop.tools.corpus import make_search_corpus_tool
from app.runtime.action_loop.types import ActionLoopContext


def build_panel_tools(
    ctx: ActionLoopContext,
    retrieval_service: Any,
    accumulate: list,
) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        make_search_corpus_tool(
            retrieval_service=retrieval_service,
            project_id=ctx.project_id,
            accumulate=accumulate,
        )
    )
    registry.register(make_get_selection_context_tool(ctx=ctx))
    return registry


__all__ = ["build_panel_tools"]
