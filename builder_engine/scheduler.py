"""Ready-set computation (orchestrate-builders SKILL §2A)."""

from __future__ import annotations

from builder_engine.graph import BuilderGraph, Packet


def compute_ready(graph: BuilderGraph) -> list[Packet]:
    """Packets ready for dispatch in the current wave."""
    ready: list[Packet] = []
    for pkt in graph.packets.values():
        if pkt.status != "ready":
            continue
        if pkt.wave != graph.wave:
            continue
        if not all(graph.packets[dep].status == "done" for dep in pkt.depends_on):
            continue
        ready.append(pkt)
    ready.sort(key=lambda p: p.id)
    return ready
