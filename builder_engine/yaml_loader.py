"""Minimal YAML loader for STATE files (no PyYAML dependency)."""

from __future__ import annotations

import re


def parse_value(s: str):
    s = s.strip()
    if not s or s == "null":
        return None
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    if s.startswith("'") and s.endswith("'"):
        return s[1:-1]
    if s in ("true", "false"):
        return s == "true"
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    return s


def load_simple_yaml(text: str) -> dict:
    root: dict = {}
    stack: list[tuple[int, dict | list]] = [(0, root)]
    key_stack: list[str | None] = [None]
    lines = text.splitlines()

    def next_content_line(idx: int) -> str | None:
        for j in range(idx + 1, len(lines)):
            s = lines[j].strip()
            if s and not s.startswith("#"):
                return lines[j]
        return None

    for i, raw_line in enumerate(lines):
        if not raw_line.strip() or raw_line.strip().startswith("#"):
            continue
        line = raw_line.split("#", 1)[0].rstrip()
        indent = len(line) - len(line.lstrip(" "))
        content = line.strip()
        while len(stack) > 1 and indent < stack[-1][0]:
            stack.pop()
            key_stack.pop()

        parent = stack[-1][1]

        if content.startswith("- "):
            item_raw = content[2:].strip()
            if not isinstance(parent, list):
                raise ValueError(f"List item without list parent: {content}")
            if ":" in item_raw and not item_raw.startswith('"'):
                k, v = item_raw.split(":", 1)
                parent.append({k.strip(): parse_value(v)})
            else:
                parent.append(parse_value(item_raw))
            continue

        if ":" not in content:
            continue
        key, val = content.split(":", 1)
        key = key.strip()
        val = val.strip()

        if val == "":
            if isinstance(parent, dict):
                nxt = next_content_line(i)
                if nxt and nxt.strip().startswith("- "):
                    new: dict | list = []
                else:
                    new = {}
                parent[key] = new
                stack.append((indent + 2, new))
                key_stack.append(key)
            continue

        if isinstance(parent, dict):
            if val.startswith("[") and val.endswith("]"):
                inner = val[1:-1].strip()
                if not inner:
                    parent[key] = []
                else:
                    parent[key] = [
                        parse_value(x.strip()) for x in inner.split(",") if x.strip()
                    ]
            elif val == "[]":
                parent[key] = []
                stack.append((indent + 2, parent[key]))
                key_stack.append(key)
            elif val == "{}":
                parent[key] = {}
                stack.append((indent + 2, parent[key]))
                key_stack.append(key)
            else:
                parent[key] = parse_value(val)

    return root
