"""Extended Plan — ready set, critical path, blockers (MB2 D3)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from builder_engine.graph import BuilderGraph, Packet
from builder_engine.scheduler import compute_ready

if TYPE_CHECKING:
    from builder_engine.observe import ObservedSnapshot
    from builder_engine.policy import PolicyDecision


class PlanError(Exception):
    """Plan cannot be built (policy block or invalid snapshot)."""


@dataclass(frozen=True)
class Plan:
    epic: str
    wave: int
    ready_packets: tuple[str, ...]
    critical_path: tuple[str, ...]
    blockers: tuple[tuple[str, str], ...]
    empty: bool


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


def critical_path(graph: BuilderGraph) -> tuple[str, ...]:
    """Longest dependency chain heuristic across all packets."""
    if not graph.packets:
        return ()

    memo: dict[str, tuple[str, ...]] = {}

    def longest(packet_id: str) -> tuple[str, ...]:
        if packet_id in memo:
            return memo[packet_id]
        pkt = graph.packets.get(packet_id)
        if pkt is None:
            return (packet_id,)
        if not pkt.depends_on:
            memo[packet_id] = (packet_id,)
            return memo[packet_id]
        best: tuple[str, ...] = (packet_id,)
        for dep in pkt.depends_on:
            chain = longest(dep)
            candidate = chain + (packet_id,)
            if len(candidate) > len(best):
                best = candidate
        memo[packet_id] = best
        return best

    return max((longest(pid) for pid in graph.packets), key=len)


def build_plan(snapshot: ObservedSnapshot, policy: PolicyDecision) -> Plan:
    """Build dispatch plan; requires policy.outcome != block."""
    if policy.outcome == "block":
        raise PlanError("policy outcome is block — cannot build plan")

    graph = BuilderGraph.load(Path(snapshot.state_path))
    ready = plan_ready(graph)
    ready_ids = tuple(p.id for p in ready)
    path = critical_path(graph)
    wave_done = wave_complete(graph)
    empty = len(ready_ids) == 0 and not wave_done

    return Plan(
        epic=snapshot.epic,
        wave=snapshot.wave,
        ready_packets=ready_ids,
        critical_path=path,
        blockers=snapshot.blockers,
        empty=empty,
    )
