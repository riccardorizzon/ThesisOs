"""Graph + ownership validation (superset of validate-state.sh, MB1 §8)."""

from __future__ import annotations

from dataclasses import dataclass, field

from builder_engine.graph import BuilderGraph, Packet


def paths_overlap(a: str, b: str) -> bool:
    return a == b or a.startswith(b) or b.startswith(a)


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def merge(self, other: ValidationResult) -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)


def validate_graph(graph: BuilderGraph) -> ValidationResult:
    result = ValidationResult()
    packets = graph.packets
    ids = set(packets.keys())

    if not graph.epic:
        result.errors.append("missing epic")
    if not packets:
        result.errors.append("no packets defined")

    for pid, pkt in packets.items():
        for dep in pkt.depends_on:
            if dep not in ids:
                result.errors.append(f"{pid}: depends_on unknown packet {dep}")
        for dep in pkt.depends_on:
            if dep not in ids:
                continue
            dep_status = packets[dep].status
            if pkt.status in ("in_progress", "done") and dep_status != "done":
                result.errors.append(
                    f"{pid}: status {pkt.status} but dependency {dep} is not done"
                )

    for path, owner in graph.file_locks.items():
        if owner not in ids:
            result.errors.append(f"file_locks: {path} owned by unknown packet {owner}")
        elif packets[owner].status not in ("in_progress", "done"):
            result.warnings.append(
                f"file_locks: {path} locked by {owner} but status is not in_progress/done"
            )

    paths_by_owner: dict[str, list[str]] = {}
    for path, owner in graph.file_locks.items():
        paths_by_owner.setdefault(owner, []).append(path)

    owners = list(paths_by_owner.keys())
    for i, owner_a in enumerate(owners):
        for owner_b in owners[i + 1 :]:
            for pa in paths_by_owner[owner_a]:
                for pb in paths_by_owner[owner_b]:
                    if paths_overlap(pa, pb):
                        result.errors.append(
                            f"path overlap between {owner_a} ({pa}) and {owner_b} ({pb})"
                        )

    _validate_wave_owned_files(graph, result)
    _validate_lock_subset(graph, result)
    _validate_wave_coherence(graph, result)
    _validate_dod_presence(graph, result)

    if not graph.decisions:
        result.warnings.append("no decisions listed — add frozen contracts / anti-goals")

    return result


def _validate_wave_owned_files(graph: BuilderGraph, result: ValidationResult) -> None:
    """§8.5 — no two packets in the same wave own overlapping paths."""
    by_wave: dict[int, list[Packet]] = {}
    for pkt in graph.packets.values():
        by_wave.setdefault(pkt.wave, []).append(pkt)

    for wave, group in by_wave.items():
        for i, a in enumerate(group):
            for b in group[i + 1 :]:
                for pa in a.owned_files:
                    for pb in b.owned_files:
                        if paths_overlap(pa, pb):
                            result.errors.append(
                                f"wave {wave}: owned_files overlap between {a.id} ({pa}) "
                                f"and {b.id} ({pb})"
                            )


def _validate_lock_subset(graph: BuilderGraph, result: ValidationResult) -> None:
    """§8.6 — locks must be subsets of owned_files for the locking packet."""
    for path, owner in graph.file_locks.items():
        pkt = graph.packets.get(owner)
        if pkt is None:
            continue
        if not pkt.owned_files:
            result.errors.append(f"file_locks: {owner} locks {path} but owns no paths")
            continue
        if not any(paths_overlap(path, owned) for owned in pkt.owned_files):
            result.errors.append(
                f"file_locks: {owner} locks {path} outside owned_files {list(pkt.owned_files)}"
            )


def _validate_wave_coherence(graph: BuilderGraph, result: ValidationResult) -> None:
    """§8.7 — in-flight packets must match STATE.wave; future-wave ready is OK."""
    for pid, pkt in graph.packets.items():
        if pkt.status == "in_progress" and pkt.wave != graph.wave:
            result.errors.append(
                f"{pid}: in_progress at wave {pkt.wave} but STATE.wave is {graph.wave}"
            )
        if pkt.status == "blocked" and pkt.wave != graph.wave:
            result.errors.append(
                f"{pid}: blocked at wave {pkt.wave} but STATE.wave is {graph.wave}"
            )
        if pkt.status == "ready" and pkt.wave < graph.wave:
            result.warnings.append(
                f"{pid}: still ready at wave {pkt.wave} but STATE.wave advanced to {graph.wave}"
            )


def _validate_dod_presence(graph: BuilderGraph, result: ValidationResult) -> None:
    """§8.8 — in_progress packets should declare checks (warn if empty)."""
    for pid, pkt in graph.packets.items():
        if pkt.status == "in_progress" and not pkt.checks:
            result.warnings.append(
                f"{pid}: in_progress without checks — add required_checks before sync (§8.8)"
            )
