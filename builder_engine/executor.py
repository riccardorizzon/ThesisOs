"""Dispatch manifest generation — executor plane (agents are external)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from builder_engine.graph import BuilderGraph, Packet


@dataclass(frozen=True)
class DispatchEntry:
    packet_id: str
    agent_type: str
    worktree_path: str
    owned_files: tuple[str, ...]
    decisions: tuple[str, ...]
    depends_on: tuple[str, ...]
    checks: tuple[str, ...]
    output: str | None
    integration_notes: str | None
    suggested_subagent_type: str

    def to_dict(self) -> dict:
        return {
            "packet_id": self.packet_id,
            "agent_type": self.agent_type,
            "worktree_path": self.worktree_path,
            "owned_files": list(self.owned_files),
            "decisions": list(self.decisions),
            "depends_on": list(self.depends_on),
            "checks": list(self.checks),
            "output": self.output,
            "integration_notes": self.integration_notes,
            "suggested_subagent_type": self.suggested_subagent_type,
        }


_AGENT_TO_SUBAGENT = {
    "explorer": "explore",
    "implementer": "generalPurpose",
    "reviewer": "generalPurpose",
    "integrator": "generalPurpose",
    "documenter": "generalPurpose",
}


def worktree_path(repo_root: Path, packet_id: str) -> Path:
    return repo_root / ".worktrees" / f"packet-{packet_id}"


def build_dispatch_entry(
    graph: BuilderGraph, packet: Packet, repo_root: Path
) -> DispatchEntry:
    dep_outputs = {
        dep: (graph.packets[dep].output or "")
        for dep in packet.depends_on
        if dep in graph.packets
    }
    notes = packet.integration_notes or ""
    if dep_outputs:
        dep_summary = "; ".join(f"{k}: {v}" for k, v in dep_outputs.items() if v)
        if dep_summary:
            notes = f"{notes} | deps: {dep_summary}".strip(" |")

    wt = worktree_path(repo_root, packet.id)
    return DispatchEntry(
        packet_id=packet.id,
        agent_type=packet.agent_type,
        worktree_path=str(wt),
        owned_files=packet.owned_files,
        decisions=tuple(graph.decisions),
        depends_on=packet.depends_on,
        checks=packet.checks,
        output=packet.output,
        integration_notes=notes or None,
        suggested_subagent_type=_AGENT_TO_SUBAGENT.get(packet.agent_type, "generalPurpose"),
    )
