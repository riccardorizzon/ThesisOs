"""Load plans/builder/STATE.yaml into a typed graph model."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from builder_engine.yaml_loader import load_simple_yaml


@dataclass(frozen=True)
class Packet:
    id: str
    wave: int
    agent_type: str
    status: str
    depends_on: tuple[str, ...]
    owned_files: tuple[str, ...]
    output: str | None = None
    checks: tuple[str, ...] = ()
    integration_notes: str | None = None

    @classmethod
    def from_mapping(cls, packet_id: str, data: dict) -> Packet:
        if not isinstance(data, dict):
            raise ValueError(f"{packet_id}: packet must be a mapping")
        return cls(
            id=packet_id,
            wave=int(data.get("wave") or 1),
            agent_type=str(data.get("agent_type") or "implementer"),
            status=str(data.get("status") or "ready"),
            depends_on=tuple(data.get("depends_on") or []),
            owned_files=tuple(data.get("owned_files") or []),
            output=data.get("output"),
            checks=tuple(data.get("checks") or []),
            integration_notes=data.get("integration_notes"),
        )


@dataclass
class BuilderGraph:
    path: Path
    epic: str
    chain: str | None
    status: str
    wave: int
    decisions: list[str] = field(default_factory=list)
    file_locks: dict[str, str] = field(default_factory=dict)
    blockers: dict[str, str] = field(default_factory=dict)
    packets: dict[str, Packet] = field(default_factory=dict)

    @classmethod
    def load(cls, state_path: Path) -> BuilderGraph:
        raw = load_simple_yaml(state_path.read_text(encoding="utf-8"))
        packets_raw = raw.get("packets") or {}
        packets = {
            pid: Packet.from_mapping(pid, pkt)
            for pid, pkt in packets_raw.items()
        }
        return cls(
            path=state_path,
            epic=str(raw.get("epic") or ""),
            chain=raw.get("chain"),
            status=str(raw.get("status") or "active"),
            wave=int(raw.get("wave") or 1),
            decisions=list(raw.get("decisions") or []),
            file_locks=dict(raw.get("file_locks") or {}),
            blockers=dict(raw.get("blockers") or {}),
            packets=packets,
        )
