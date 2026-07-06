"""Load Governance Program Graph declarations (MB2 SoR §4.1)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from builder_engine.yaml_loader import load_simple_yaml

DONE_STATUSES = frozenset({"done", "implemented"})


@dataclass(frozen=True)
class WorkOrderNode:
    id: str
    depends_on: tuple[str, ...]
    status: str = "ready"
    wave: str | None = None

    @property
    def program_graph_ref(self) -> str:
        return self.id


@dataclass(frozen=True)
class WaveSpec:
    id: str
    workorders: tuple[str, ...]
    merge_order: tuple[str, ...]
    execute_in_parallel: bool = False


@dataclass(frozen=True)
class ProgramGraph:
    program_id: str
    workorders: dict[str, WorkOrderNode]
    waves: dict[str, WaveSpec]

    def workorder_ids(self) -> frozenset[str]:
        return frozenset(self.workorders)


def _as_str_tuple(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (list, tuple)):
        return tuple(str(item) for item in value)
    return (str(value),)


def _parse_inline_list(raw: str) -> tuple[str, ...]:
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return ()
        return tuple(part.strip() for part in inner.split(",") if part.strip())
    return (raw,) if raw else ()


def _parse_workorder(entry: dict | str) -> WorkOrderNode:
    if isinstance(entry, str):
        return WorkOrderNode(id=entry, depends_on=())
    if not isinstance(entry, dict):
        raise ValueError(f"workorder entry must be mapping or id string, got {type(entry)}")
    ewo_id = entry.get("id")
    if not ewo_id:
        raise ValueError("workorder entry missing id")
    return WorkOrderNode(
        id=str(ewo_id),
        depends_on=_as_str_tuple(entry.get("depends_on")),
        status=str(entry.get("status") or "ready"),
        wave=str(entry["wave"]) if entry.get("wave") else None,
    )


def _parse_wave(wave_id: str, data: dict) -> WaveSpec:
    workorders = _as_str_tuple(data.get("workorders"))
    merge_order = _as_str_tuple(data.get("merge_order"))
    if merge_order and not workorders:
        workorders = merge_order
    return WaveSpec(
        id=wave_id,
        workorders=workorders,
        merge_order=merge_order or workorders,
        execute_in_parallel=bool(data.get("execute_in_parallel")),
    )


def _parse_workorder_backlog_section(text: str) -> dict[str, WorkOrderNode]:
    """Line parser for indented workorder_backlog list entries."""
    lines = text.splitlines()
    start = next(
        (idx for idx, line in enumerate(lines) if line.strip().startswith("workorder_backlog:")),
        None,
    )
    if start is None:
        return {}

    workorders: dict[str, WorkOrderNode] = {}
    current_id: str | None = None
    depends_on: tuple[str, ...] = ()
    status = "ready"
    wave: str | None = None
    section_indent = len(lines[start]) - len(lines[start].lstrip())

    def flush() -> None:
        nonlocal current_id, depends_on, status, wave
        if not current_id:
            return
        if current_id in workorders:
            raise ValueError(f"duplicate workorder id {current_id!r}")
        workorders[current_id] = WorkOrderNode(
            id=current_id,
            depends_on=depends_on,
            status=status,
            wave=wave,
        )
        current_id = None
        depends_on = ()
        status = "ready"
        wave = None

    for line in lines[start + 1 :]:
        if not line.strip() or line.strip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if indent <= section_indent and not line.lstrip().startswith("- "):
            break
        stripped = line.strip()
        if stripped.startswith("- id:"):
            flush()
            current_id = stripped.split(":", 1)[1].strip()
            continue
        if current_id is None:
            continue
        if stripped.startswith("depends_on:"):
            depends_on = _parse_inline_list(stripped.split(":", 1)[1])
        elif stripped.startswith("status:"):
            status = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("wave:"):
            wave = stripped.split(":", 1)[1].strip()

    flush()
    return workorders


def _parse_workorders_dict(raw: dict) -> dict[str, WorkOrderNode]:
    workorders: dict[str, WorkOrderNode] = {}
    for ewo_id, data in raw.items():
        if isinstance(data, dict):
            node = WorkOrderNode(
                id=str(ewo_id),
                depends_on=_as_str_tuple(data.get("depends_on")),
                status=str(data.get("status") or "ready"),
                wave=str(data["wave"]) if data.get("wave") else None,
            )
        else:
            node = WorkOrderNode(id=str(ewo_id), depends_on=())
        if node.id in workorders:
            raise ValueError(f"duplicate workorder id {node.id!r}")
        workorders[node.id] = node
    return workorders


def validate_program_graph(graph: ProgramGraph) -> None:
    _validate_references(graph)
    _detect_cycles(graph)


def _validate_references(graph: ProgramGraph) -> None:
    known = graph.workorder_ids()
    for node in graph.workorders.values():
        for dep in node.depends_on:
            if dep not in known:
                raise ValueError(f"unknown dependency {dep!r} for workorder {node.id!r}")
    for wave in graph.waves.values():
        for ewo_id in wave.workorders:
            if ewo_id not in known:
                raise ValueError(f"wave {wave.id!r} references unknown workorder {ewo_id!r}")
        for ewo_id in wave.merge_order:
            if ewo_id not in known:
                raise ValueError(f"merge_order references unknown workorder {ewo_id!r}")


def _detect_cycles(graph: ProgramGraph) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in visiting:
            raise ValueError(f"circular depends_on involving {node_id!r}")
        if node_id in visited:
            return
        visiting.add(node_id)
        node = graph.workorders[node_id]
        for dep in node.depends_on:
            visit(dep)
        visiting.remove(node_id)
        visited.add(node_id)

    for ewo_id in graph.workorders:
        visit(ewo_id)


def load_program_graph(path: Path) -> ProgramGraph:
    text = path.read_text(encoding="utf-8")
    raw = load_simple_yaml(text)
    program_id = str(raw.get("id") or path.stem)

    workorders = _parse_workorder_backlog_section(text)
    if not workorders:
        backlog_raw = raw.get("workorder_backlog") or []
        if isinstance(backlog_raw, list):
            for entry in backlog_raw:
                node = _parse_workorder(entry)
                if node.id in workorders:
                    raise ValueError(f"duplicate workorder id {node.id!r}")
                workorders[node.id] = node
    workorders_dict = raw.get("workorders")
    if isinstance(workorders_dict, dict):
        for ewo_id, node in _parse_workorders_dict(workorders_dict).items():
            workorders[ewo_id] = node

    if not workorders:
        raise ValueError(f"no workorders found in program graph: {path}")

    waves_raw = raw.get("waves") or {}
    waves: dict[str, WaveSpec] = {}
    if isinstance(waves_raw, dict):
        for wave_id, wave_data in waves_raw.items():
            if isinstance(wave_data, dict):
                waves[str(wave_id)] = _parse_wave(str(wave_id), wave_data)

    graph = ProgramGraph(program_id=program_id, workorders=workorders, waves=waves)
    validate_program_graph(graph)
    return graph


def load_program_graph_from_repo(repo_root: Path, program_id: str) -> ProgramGraph:
    path = repo_root / ".asep" / "programs" / f"{program_id}.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"program graph not found: {path}")
    graph = load_program_graph(path)
    if graph.program_id != program_id and path.stem == program_id:
        return ProgramGraph(
            program_id=program_id,
            workorders=graph.workorders,
            waves=graph.waves,
        )
    return graph
