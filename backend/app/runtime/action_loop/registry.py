from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolSpec:
    name: str
    fn: Callable[..., Any]
    schema: dict[str, Any]


def _default_schema(name: str, fn: Callable[..., Any]) -> dict[str, Any]:
    doc = (fn.__doc__ or "").strip() or f"Tool {name}"
    sig = inspect.signature(fn)
    properties: dict[str, Any] = {}
    required: list[str] = []
    for param_name, param in sig.parameters.items():
        if param_name in {"self", "cls"}:
            continue
        if param.annotation is int:
            prop: dict[str, Any] = {"type": "integer"}
        elif param.annotation is float:
            prop = {"type": "number"}
        elif param.annotation is bool:
            prop = {"type": "boolean"}
        else:
            prop = {"type": "string"}
        if param.default is inspect.Parameter.empty:
            required.append(param_name)
        properties[param_name] = prop
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": doc,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(
        self,
        fn: Callable[..., Any],
        *,
        name: str | None = None,
        schema: dict[str, Any] | None = None,
    ) -> None:
        tool_name = name or fn.__name__
        tool_schema = schema or _default_schema(tool_name, fn)
        self._tools[tool_name] = ToolSpec(name=tool_name, fn=fn, schema=tool_schema)

    def execute(self, name: str, arguments: dict[str, Any]) -> Any:
        spec = self._tools.get(name)
        if spec is None:
            raise KeyError(f"Unknown tool: {name}")
        return spec.fn(**arguments)

    def schemas(self) -> list[dict[str, Any]]:
        return [spec.schema for spec in self._tools.values()]
