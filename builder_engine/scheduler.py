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


def in_flight_packets(graph: BuilderGraph) -> list[Packet]:
    """Packets currently in_progress (CLAIMED/RUNNING/VALIDATING in ADR-0025)."""
    return sorted(
        (p for p in graph.packets.values() if p.status == "in_progress"),
        key=lambda p: p.id,
    )


def file_locks_for_packet(packet: Packet) -> dict[str, str]:
    """Lock map for owned paths when a packet is scheduled."""
    return {path: packet.id for path in packet.owned_files}
