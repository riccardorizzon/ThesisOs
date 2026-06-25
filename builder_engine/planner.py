"""Planner — derive ready work from graph state (Phase 2 stub; replan in Phase 4)."""

from __future__ import annotations

from builder_engine.graph import BuilderGraph, Packet
from builder_engine.scheduler import compute_ready


def plan_ready(graph: BuilderGraph) -> list[Packet]:
    """Packets eligible for dispatch in the current wave."""
    return compute_ready(graph)


def wave_complete(graph: BuilderGraph, wave: int | None = None) -> bool:
    """True when every packet in the wave is done."""
    target = wave if wave is not None else graph.wave
    wave_packets = [p for p in graph.packets.values() if p.wave == target]
    if not wave_packets:
        return True
    return all(p.status == "done" for p in wave_packets)


def next_wave(graph: BuilderGraph) -> int | None:
    """Next wave number after current, or None if no higher waves exist."""
    waves = {p.wave for p in graph.packets.values()}
    higher = [w for w in waves if w > graph.wave]
    return min(higher) if higher else None


def wave_complete_raw(raw: dict, wave: int | None = None) -> bool:
    """True when every packet in the wave is done (raw STATE dict)."""
    target = wave if wave is not None else int(raw.get("wave") or 1)
    packets = raw.get("packets") or {}
    wave_packets = [
        p
        for p in packets.values()
        if isinstance(p, dict) and int(p.get("wave") or 1) == target
    ]
    if not wave_packets:
        return True
    return all(p.get("status") == "done" for p in wave_packets)


def next_wave_from_raw(raw: dict) -> int | None:
    """Next wave after current in raw STATE, or None."""
    current = int(raw.get("wave") or 1)
    waves = {
        int(p.get("wave") or 1)
        for p in (raw.get("packets") or {}).values()
        if isinstance(p, dict)
    }
    higher = [w for w in waves if w > current]
    return min(higher) if higher else None
