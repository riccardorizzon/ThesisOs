"""Load and atomically persist plans/builder/STATE.yaml."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from builder_engine.yaml_loader import load_simple_yaml


def load_raw_state(path: Path) -> dict[str, Any]:
    return load_simple_yaml(path.read_text(encoding="utf-8"))


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


def _yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        if not value:
            return '""'
        if any(c in value for c in ':"[]{}#&*!|>%@`'):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        return value
    return repr(value)


def dump_state(data: dict[str, Any]) -> str:
    """Serialize STATE dict to YAML (comments not preserved)."""
    lines: list[str] = []

    def emit(line: str = "") -> None:
        lines.append(line)

    emit(f"epic: {_yaml_scalar(data.get('epic', ''))}")
    if data.get("chain") is not None:
        emit(f"chain: {_yaml_scalar(data['chain'])}")
    emit(f"status: {_yaml_scalar(data.get('status', 'active'))}")
    emit(f"wave: {int(data.get('wave') or 1)}")
    emit("")
    emit("decisions:")
    for item in data.get("decisions") or []:
        emit(f"  - {_yaml_scalar(item)}")
    emit("")
    emit("file_locks:")
    locks = data.get("file_locks") or {}
    if not locks:
        emit("  {}")
    else:
        for path, owner in sorted(locks.items()):
            emit(f"  {_yaml_scalar(path)}: {_yaml_scalar(owner)}")
    emit("")
    emit("blockers:")
    blockers = data.get("blockers") or {}
    if not blockers:
        emit("  {}")
    else:
        for pid, desc in sorted(blockers.items()):
            emit(f"  {_yaml_scalar(pid)}: {_yaml_scalar(desc)}")
    emit("")
    emit("packets:")
    for pid, pkt in sorted((data.get("packets") or {}).items()):
        if not isinstance(pkt, dict):
            continue
        emit(f"  {pid}:")
        emit(f"    wave: {int(pkt.get('wave') or 1)}")
        emit(f"    agent_type: {_yaml_scalar(pkt.get('agent_type', 'implementer'))}")
        emit(f"    status: {_yaml_scalar(pkt.get('status', 'ready'))}")
        deps = pkt.get("depends_on") or []
        if deps:
            inner = ", ".join(_yaml_scalar(d) for d in deps)
            emit(f"    depends_on: [{inner}]")
        else:
            emit("    depends_on: []")
        owned = pkt.get("owned_files") or []
        emit("    owned_files:")
        for path in owned:
            emit(f"      - {_yaml_scalar(path)}")
        if pkt.get("output") is not None:
            emit(f"    output: {_yaml_scalar(pkt['output'])}")
        checks = pkt.get("checks") or []
        if checks:
            inner = ", ".join(_yaml_scalar(c) for c in checks)
            emit(f"    checks: [{inner}]")
        else:
            emit("    checks: []")
        if pkt.get("integration_notes") is not None:
            emit(f"    integration_notes: {_yaml_scalar(pkt['integration_notes'])}")
        emit("")
    return "\n".join(lines).rstrip() + "\n"


def save_raw_state(path: Path, data: dict[str, Any], *, skip_invariant_check: bool = False) -> None:
    if not skip_invariant_check:
        from builder_engine.invariants import check_raw_state

        check_raw_state(data, path)
    atomic_write_text(path, dump_state(data))
