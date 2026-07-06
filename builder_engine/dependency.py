"""Derive Execution Graph from Program Graph (MB2 SoR §4.2)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from builder_engine.events import BuildEventBus, event_now
from builder_engine.program_graph import (
    DONE_STATUSES,
    ProgramGraph,
    WorkOrderNode,
)


@dataclass(frozen=True)
class ExecutionNode:
    ewo_id: str
    program_graph_ref: str
    depends_on: tuple[str, ...]
    wave: str | None
    state: str
    ready: bool


@dataclass
class ExecutionGraph:
    program_id: str
    nodes: dict[str, ExecutionNode] = field(default_factory=dict)
    graph_hash: str = ""

    def node_ids(self) -> list[str]:
        return list(self.nodes)


class DependencyEngine:
    """Derive-only Execution Graph builder — no manual graph mutation (INV-R-02)."""

    def __init__(
        self,
        program: ProgramGraph,
        completion_state: dict[str, str] | None = None,
        *,
        bus: BuildEventBus | None = None,
        cycle_id: str | None = None,
    ) -> None:
        from builder_engine.program_graph import validate_program_graph

        validate_program_graph(program)
        self.program = program
        self.completion_state = completion_state or {}
        self.bus = bus
        self.cycle_id = cycle_id
        self._graph: ExecutionGraph | None = None

    def derive(self, *, publish: bool = True) -> ExecutionGraph:
        nodes: dict[str, ExecutionNode] = {}
        for ewo_id, wo in self.program.workorders.items():
            state = self._resolve_state(wo)
            nodes[ewo_id] = ExecutionNode(
                ewo_id=ewo_id,
                program_graph_ref=wo.program_graph_ref,
                depends_on=wo.depends_on,
                wave=wo.wave,
                state=state,
                ready=self._is_ready(wo, state),
            )

        graph_hash = _content_hash(nodes)
        graph = ExecutionGraph(
            program_id=self.program.program_id,
            nodes=nodes,
            graph_hash=graph_hash,
        )
        self._graph = graph

        if publish and self.bus is not None:
            ready = self.ready_set(graph)
            self.bus.publish(
                event_now(
                    "ExecutionGraphDerived",
                    {
                        "program_id": self.program.program_id,
                        "graph_hash": graph_hash,
                        "ready_count": len(ready),
                        "node_ids": list(nodes.keys()),
                    },
                    program_id=self.program.program_id,
                    cycle_id=self.cycle_id,
                )
            )
        return graph

    def ready_set(self, graph: ExecutionGraph | None = None) -> list[ExecutionNode]:
        graph = graph or self._require_graph()
        ready = [node for node in graph.nodes.values() if node.ready]
        return _apply_merge_order(ready, self.program)

    def critical_path(self, graph: ExecutionGraph | None = None) -> list[ExecutionNode]:
        graph = graph or self._require_graph()
        pending = [
            node
            for node in graph.nodes.values()
            if node.state not in DONE_STATUSES and node.state != "cancelled"
        ]
        ordered = _topological_pending(pending)
        return _apply_merge_order(ordered, self.program)

    def _require_graph(self) -> ExecutionGraph:
        if self._graph is None:
            raise RuntimeError("call derive() before ready_set() or critical_path()")
        return self._graph

    def _resolve_state(self, wo: WorkOrderNode) -> str:
        return self.completion_state.get(wo.id, wo.status)

    def _is_ready(self, wo: WorkOrderNode, state: str) -> bool:
        if state in DONE_STATUSES or state in {"blocked", "cancelled", "in_progress"}:
            return False
        if state != "ready":
            return False
        return all(self._dependency_satisfied(dep) for dep in wo.depends_on)

    def _dependency_satisfied(self, dep_id: str) -> bool:
        if dep_id not in self.program.workorders:
            raise ValueError(f"orphan dependency {dep_id!r} — not in Program Graph")
        dep_state = self._resolve_state(self.program.workorders[dep_id])
        return dep_state in DONE_STATUSES


def _content_hash(nodes: dict[str, ExecutionNode]) -> str:
    payload = {
        ewo_id: {
            "program_graph_ref": node.program_graph_ref,
            "depends_on": list(node.depends_on),
            "wave": node.wave,
            "state": node.state,
            "ready": node.ready,
        }
        for ewo_id, node in sorted(nodes.items())
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _merge_rank(program: ProgramGraph, ewo_id: str) -> tuple[int, int]:
    for wave_idx, wave in enumerate(program.waves.values()):
        if ewo_id in wave.merge_order:
            return (wave_idx, wave.merge_order.index(ewo_id))
    return (len(program.waves), 0)


def _apply_merge_order(nodes: list[ExecutionNode], program: ProgramGraph) -> list[ExecutionNode]:
    return sorted(nodes, key=lambda n: (_merge_rank(program, n.ewo_id), n.ewo_id))


def _topological_pending(nodes: list[ExecutionNode]) -> list[ExecutionNode]:
    by_id = {node.ewo_id: node for node in nodes}
    indegree = {node.ewo_id: 0 for node in nodes}
    for node in nodes:
        for dep in node.depends_on:
            if dep in by_id:
                indegree[node.ewo_id] += 1

    queue = sorted([ewo_id for ewo_id, deg in indegree.items() if deg == 0])
    ordered: list[ExecutionNode] = []
    while queue:
        current = queue.pop(0)
        ordered.append(by_id[current])
        for node in nodes:
            if current in node.depends_on and node.ewo_id in indegree:
                indegree[node.ewo_id] -= 1
                if indegree[node.ewo_id] == 0 and node.ewo_id not in {n.ewo_id for n in ordered}:
                    queue.append(node.ewo_id)
                    queue.sort()

    for node in nodes:
        if node not in ordered:
            ordered.append(node)
    return ordered
