#!/usr/bin/env bash
# Validate plans/builder/STATE.yaml consistency.
# Prefers builder-engine lint-graph (MB1 Phase 1); falls back to inline validator.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../../../" && pwd)"
STATE_FILE="${1:-$ROOT/plans/builder/STATE.yaml}"

if command -v builder-engine >/dev/null 2>&1; then
  exec builder-engine lint-graph --state "$STATE_FILE" --repo-root "$ROOT"
fi

ENGINE="$ROOT/builder_engine/.venv/bin/builder-engine"
if [[ -x "$ENGINE" ]]; then
  exec "$ENGINE" lint-graph --state "$STATE_FILE" --repo-root "$ROOT"
fi

# Fallback: inline Python (legacy, no MB1 §8.5–8.8 invariants)
python3 - "$STATE_FILE" <<'PY'
import re
import sys
from pathlib import Path

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

state_path = Path(sys.argv[1])
try:
    data = load_simple_yaml(state_path.read_text())
except Exception as e:
    print(f"ERROR: failed to parse {state_path}: {e}")
    sys.exit(1)

errors: list[str] = []
warnings: list[str] = []

packets = data.get("packets") or {}
file_locks = data.get("file_locks") or {}
decisions = data.get("decisions") or []

if not data.get("epic"):
    errors.append("missing epic")
if not packets:
    errors.append("no packets defined")

ids = set(packets.keys())
for pid, pkt in packets.items():
    if not isinstance(pkt, dict):
        errors.append(f"{pid}: packet must be a mapping")
        continue
    for dep in pkt.get("depends_on") or []:
        if dep not in ids:
            errors.append(f"{pid}: depends_on unknown packet {dep}")
    status = pkt.get("status", "ready")
    for dep in pkt.get("depends_on") or []:
        dep_status = (packets.get(dep) or {}).get("status")
        if status in ("in_progress", "done") and dep_status != "done":
            errors.append(f"{pid}: status {status} but dependency {dep} is not done")

for path, owner in file_locks.items():
    if owner not in ids:
        errors.append(f"file_locks: {path} owned by unknown packet {owner}")
    elif packets[owner].get("status") not in ("in_progress", "done"):
        warnings.append(
            f"file_locks: {path} locked by {owner} but status is not in_progress/done"
        )

paths_by_owner: dict[str, list[str]] = {}
for path, owner in file_locks.items():
    paths_by_owner.setdefault(owner, []).append(path)

owners = list(paths_by_owner.keys())
for i, a in enumerate(owners):
    for b in owners[i + 1:]:
        for pa in paths_by_owner[a]:
            for pb in paths_by_owner[b]:
                if pa == pb or pa.startswith(pb) or pb.startswith(pa):
                    errors.append(f"path overlap between {a} ({pa}) and {b} ({pb})")

if not decisions:
    warnings.append("no decisions listed — add frozen contracts / anti-goals")

in_progress = [p for p, pkt in packets.items() if pkt.get("status") == "in_progress"]

print(f"STATE: {state_path}")
print(
    f"Epic: {data.get('epic', '?')} | Wave: {data.get('wave', '?')} | "
    f"Packets: {len(packets)}"
)
print(
    f"Decisions: {len(decisions)} | File locks: {len(file_locks)} | "
    f"In progress: {len(in_progress)}"
)

for w in warnings:
    print(f"WARN: {w}")
for e in errors:
    print(f"ERROR: {e}")

if errors:
    print(f"\nValidation FAILED ({len(errors)} errors)")
    sys.exit(1)

print("\nValidation OK")
PY
