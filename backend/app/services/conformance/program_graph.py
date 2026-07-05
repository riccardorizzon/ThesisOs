"""Read-only Program Graph parser (PX3-EWO-008, SoR §4.1 / §4.2 boundary)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from app.schemas.program_graph import (
    ExecutionNodeObservation,
    GraphEdgeObservation,
    ProgramGraphObservationV1,
    WaveObservation,
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    return loaded if isinstance(loaded, dict) else {}


def _node_type(wave_type: str | None) -> str:
    if wave_type in ("integration", "conformance_integration"):
        return "integration"
    return "ewo"


def build_program_graph_observation(
    *, root: Path | None = None
) -> ProgramGraphObservationV1:
    """Parse px3-parallel.yaml — observe Program→Execution structure; no ReadySet."""
    base = root or repo_root()
    parallel_path = base / ".asep/programs/px3-parallel.yaml"
    parallel = _load_yaml(parallel_path)

    waves: list[WaveObservation] = []
    edges: list[GraphEdgeObservation] = []

    for wave_id, wave_def in (parallel.get("waves") or {}).items():
        if not isinstance(wave_def, dict):
            continue

        workorders = [
            w for w in (wave_def.get("workorders") or []) if isinstance(w, str)
        ]
        merge_order = [
            m for m in (wave_def.get("merge_order") or []) if isinstance(m, str)
        ]
        depends_on = wave_def.get("depends_on_wave")
        wave_type = wave_def.get("type")
        ntype = _node_type(wave_type if isinstance(wave_type, str) else None)

        nodes = [
            ExecutionNodeObservation(
                node_id=ewo_id, node_type=ntype, wave_id=str(wave_id)
            )
            for ewo_id in workorders
        ]

        sub_agents_raw = wave_def.get("sub_agents") or {}
        sub_agents = {
            str(k): str(v)
            for k, v in sub_agents_raw.items()
            if isinstance(k, str)
        }

        waves.append(
            WaveObservation(
                wave_id=str(wave_id),
                title=str(wave_def.get("title", wave_id)),
                depends_on_wave=str(depends_on) if depends_on else None,
                execute_in_parallel=bool(wave_def.get("execute_in_parallel", False)),
                merge_order=merge_order,
                workorders=workorders,
                unblocks=(
                    str(wave_def["unblocks"])
                    if wave_def.get("unblocks") is not None
                    else None
                ),
                wave_type=wave_type if isinstance(wave_type, str) else None,
                status=wave_def.get("status") if isinstance(wave_def.get("status"), str) else None,
                sub_agents=sub_agents,
                nodes=nodes,
            )
        )

        if depends_on:
            edges.append(
                GraphEdgeObservation(
                    source=str(depends_on),
                    target=str(wave_id),
                    edge_type="depends_on_wave",
                )
            )

        for idx in range(len(merge_order) - 1):
            edges.append(
                GraphEdgeObservation(
                    source=merge_order[idx],
                    target=merge_order[idx + 1],
                    edge_type="merge_order",
                    wave_id=str(wave_id),
                )
            )

    return ProgramGraphObservationV1(
        program_id=str(parallel.get("id", "px3-parallel")),
        parent_program=str(parallel.get("parent_program", "")),
        source=".asep/programs/px3-parallel.yaml",
        waves=waves,
        edges=edges,
    )
