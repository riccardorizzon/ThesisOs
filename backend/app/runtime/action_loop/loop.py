from __future__ import annotations

import inspect
import json
from collections.abc import Awaitable, Callable
from typing import Any

from app.runtime.action_loop.permissions import PermissionEngine
from app.runtime.action_loop.registry import ToolRegistry
from app.runtime.action_loop.risk import classify
from app.runtime.action_loop.types import AssistantTurn, LoopResult, LoopStep, ToolCallRecord


class ActionLoopRunner:
    def __init__(
        self,
        *,
        registry: ToolRegistry,
        permissions: PermissionEngine,
        complete: Callable[[list[dict[str, Any]], list[dict[str, Any]]], Awaitable[AssistantTurn]],
        max_iterations: int = 6,
    ) -> None:
        self._registry = registry
        self._permissions = permissions
        self._complete = complete
        self._max_iterations = max_iterations

    async def run(
        self,
        messages: list[dict[str, Any]],
        *,
        on_step: Callable[[LoopStep], None] | None = None,
    ) -> LoopResult:
        history = list(messages)
        tools = self._registry.schemas()
        steps: list[LoopStep] = []
        tool_records: list[ToolCallRecord] = []

        for _ in range(self._max_iterations):
            turn = await self._complete(history, tools)

            if not turn.tool_calls:
                break

            assistant_message: dict[str, Any] = {
                "role": "assistant",
                "content": turn.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": json.dumps(tc.arguments),
                        },
                    }
                    for tc in turn.tool_calls
                ],
            }
            history.append(assistant_message)

            for tc in turn.tool_calls:
                risk = classify(tc.name)
                decision = self._permissions.check(tc.name, tc.arguments, risk)
                if not decision.allowed:
                    raise PermissionError(f"Tool not allowed: {tc.name}")

                step = LoopStep(label=f"Esecuzione {tc.name}", detail=str(tc.arguments.get("query", "")) or None)
                steps.append(step)
                if on_step is not None:
                    on_step(step)

                result = self._registry.execute(tc.name, tc.arguments)
                if inspect.iscoroutine(result):
                    result = await result
                result_summary = json.dumps(result)[:200] if not isinstance(result, str) else result[:200]
                tool_records.append(
                    ToolCallRecord(name=tc.name, arguments=tc.arguments, result_summary=result_summary)
                )

                history.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result) if not isinstance(result, str) else result,
                    }
                )
        else:
            raise RuntimeError(f"Action loop exceeded max iterations ({self._max_iterations})")

        return LoopResult(chunks=[], steps=steps, tool_calls=tool_records)
