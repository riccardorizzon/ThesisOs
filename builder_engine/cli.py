"""Build Workflow Engine CLI — projections on EngineeringRuntime (ADR-0025)."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from builder_engine.checks import run_stage
from builder_engine.graph import BuilderGraph
from builder_engine.cycle import CycleError, EngineeringRuntimeCycle
from builder_engine.events import BuildEventBus
from builder_engine.merge import merge_eligibility
from builder_engine.observe import StateObserver
from builder_engine.paths import default_state_path, find_repo_root
from builder_engine.planner import PlanError, build_plan
from builder_engine.policy import PolicyEngine
from builder_engine.runtime import EngineeringRuntime, EngineeringRuntimeError
from builder_engine.scheduler import compute_ready
from builder_engine.validate import validate_graph

app = typer.Typer(
    name="builder-engine",
    help="ThesisOS Build Workflow Engine — deterministic BuilderOS orchestration (ADR-0023).",
)
console = Console()


def _root(repo_root: Optional[Path]) -> Path:
    return repo_root or find_repo_root()


def _load(state: Optional[Path], repo_root: Path) -> BuilderGraph:
    state_path = state or default_state_path(repo_root)
    if not state_path.is_file():
        console.print(f"[red]STATE file not found:[/red] {state_path}")
        raise typer.Exit(1)
    try:
        return BuilderGraph.load(state_path)
    except Exception as exc:
        console.print(f"[red]Failed to parse STATE:[/red] {exc}")
        raise typer.Exit(1) from exc


@app.command("lint-graph")
def lint_graph(
    state: Optional[Path] = typer.Option(None, "--state", help="Path to STATE.yaml"),
    repo_root: Optional[Path] = typer.Option(None, "--repo-root"),
) -> None:
    """Validate STATE graph, ownership, and wave invariants."""
    root = _root(repo_root)
    graph = _load(state, root)
    result = validate_graph(graph)

    in_progress = [p for p, pkt in graph.packets.items() if pkt.status == "in_progress"]
    console.print(f"STATE: {graph.path}")
    console.print(
        f"Epic: {graph.epic} | Wave: {graph.wave} | Packets: {len(graph.packets)}"
    )
    console.print(
        f"Decisions: {len(graph.decisions)} | File locks: {len(graph.file_locks)} | "
        f"In progress: {len(in_progress)}"
    )

    for warning in result.warnings:
        console.print(f"[yellow]WARN:[/yellow] {warning}")
    for error in result.errors:
        console.print(f"[red]ERROR:[/red] {error}")

    if not result.ok:
        console.print(f"\n[red]Validation FAILED ({len(result.errors)} errors)[/red]")
        raise typer.Exit(1)

    console.print("\n[green]Validation OK[/green]")


@app.command()
def status(
    state: Optional[Path] = typer.Option(None, "--state"),
    repo_root: Optional[Path] = typer.Option(None, "--repo-root"),
) -> None:
    """Print STATE summary."""
    root = _root(repo_root)
    graph = _load(state, root)
    result = validate_graph(graph)

    table = Table(title=f"Builder STATE — {graph.epic}")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("path", str(graph.path))
    table.add_row("chain", graph.chain or "—")
    table.add_row("status", graph.status)
    table.add_row("wave", str(graph.wave))
    table.add_row("packets", str(len(graph.packets)))
    table.add_row("decisions", str(len(graph.decisions)))
    table.add_row("file_locks", str(len(graph.file_locks)))
    table.add_row("blockers", str(len(graph.blockers)))
    table.add_row("validation", "OK" if result.ok else f"{len(result.errors)} errors")
    console.print(table)

    pkt_table = Table(title="Packets")
    pkt_table.add_column("ID")
    pkt_table.add_column("Wave")
    pkt_table.add_column("Status")
    pkt_table.add_column("Agent")
    pkt_table.add_column("Depends")
    for pid in sorted(graph.packets):
        pkt = graph.packets[pid]
        pkt_table.add_row(
            pid,
            str(pkt.wave),
            pkt.status,
            pkt.agent_type,
            ", ".join(pkt.depends_on) or "—",
        )
    console.print(pkt_table)

    if graph.file_locks:
        lock_table = Table(title="File locks")
        lock_table.add_column("Path")
        lock_table.add_column("Owner")
        for path, owner in sorted(graph.file_locks.items()):
            lock_table.add_row(path, owner)
        console.print(lock_table)

    if graph.blockers:
        for pid, desc in graph.blockers.items():
            console.print(f"[red]BLOCKER[/red] {pid}: {desc}")

    if not result.ok:
        raise typer.Exit(1)


@app.command()
def observe(
    state: Optional[Path] = typer.Option(None, "--state"),
    repo_root: Optional[Path] = typer.Option(None, "--repo-root"),
    json_out: bool = typer.Option(False, "--json", help="Emit ObservedSnapshot as JSON"),
) -> None:
    """Observe workflow + git state into an immutable snapshot (MB2 D1, read-only)."""
    root = _root(repo_root)
    state_path = state or default_state_path(root)
    snapshot = StateObserver(root, state_path).observe()

    if json_out:
        import json

        payload = {
            "observed_at": snapshot.observed_at,
            "state_path": snapshot.state_path,
            "epic": snapshot.epic,
            "chain": snapshot.chain,
            "epic_status": snapshot.epic_status,
            "wave": snapshot.wave,
            "packet_count": snapshot.packet_count,
            "ready_count": snapshot.ready_count,
            "in_flight_count": snapshot.in_flight_count,
            "done_count": snapshot.done_count,
            "blocked_count": snapshot.blocked_count,
            "decisions_count": snapshot.decisions_count,
            "file_locks": dict(snapshot.file_locks),
            "blockers": dict(snapshot.blockers),
            "packets": [
                {
                    "id": p.id,
                    "wave": p.wave,
                    "status": p.status,
                    "agent_type": p.agent_type,
                    "depends_on": list(p.depends_on),
                    "checks": list(p.checks),
                }
                for p in snapshot.packets
            ],
            "git": {
                "is_repo": snapshot.git.is_repo,
                "branch": snapshot.git.branch,
                "dirty": snapshot.git.dirty,
                "uncommitted_count": snapshot.git.uncommitted_count,
            },
            "validation_ok": snapshot.validation_ok,
            "validation_errors": list(snapshot.validation_errors),
            "validation_warnings": list(snapshot.validation_warnings),
            "staleness_reasons": list(snapshot.staleness_reasons),
            "is_complete": snapshot.is_complete,
        }
        console.print_json(json.dumps(payload))
        if not snapshot.is_complete:
            raise typer.Exit(1)
        return

    table = Table(title="Observed Snapshot")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("observed_at", snapshot.observed_at)
    table.add_row("epic", snapshot.epic or "—")
    table.add_row("status", snapshot.epic_status or "—")
    table.add_row("wave", str(snapshot.wave))
    table.add_row("packets", str(snapshot.packet_count))
    table.add_row("ready", str(snapshot.ready_count))
    table.add_row("in_flight", str(snapshot.in_flight_count))
    table.add_row("done", str(snapshot.done_count))
    table.add_row("validation", "OK" if snapshot.validation_ok else "FAIL")
    if snapshot.git.is_repo:
        table.add_row("git branch", snapshot.git.branch or "—")
        table.add_row("git dirty", str(snapshot.git.dirty))
    table.add_row("is_complete", str(snapshot.is_complete))
    console.print(table)

    if snapshot.validation_errors:
        for err in snapshot.validation_errors:
            console.print(f"[red]ERROR:[/red] {err}")
    for warn in snapshot.validation_warnings:
        console.print(f"[yellow]WARN:[/yellow] {warn}")
    for reason in snapshot.staleness_reasons:
        console.print(f"[red]STALE:[/red] {reason}")

    if not snapshot.is_complete:
        raise typer.Exit(1)


@app.command()
def policy(
    state: Optional[Path] = typer.Option(None, "--state"),
    repo_root: Optional[Path] = typer.Option(None, "--repo-root"),
    json_out: bool = typer.Option(False, "--json", help="Emit PolicyDecision as JSON"),
) -> None:
    """Evaluate policies after Observe (MB2 D2, read-only)."""
    root = _root(repo_root)
    state_path = state or default_state_path(root)
    snapshot = StateObserver(root, state_path).observe()
    decision = PolicyEngine(root).evaluate(snapshot)

    if json_out:
        import json

        payload = {
            "outcome": decision.outcome,
            "violations": [
                {"rule_id": v.rule_id, "message": v.message, "action": v.action}
                for v in decision.violations
            ],
            "warnings": list(decision.warnings),
        }
        console.print_json(json.dumps(payload))
        if decision.outcome == "block":
            raise typer.Exit(1)
        return

    table = Table(title="Policy Decision")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("outcome", decision.outcome)
    table.add_row("violations", str(len(decision.violations)))
    table.add_row("warnings", str(len(decision.warnings)))
    console.print(table)

    for v in decision.violations:
        color = {"block": "red", "escalate": "yellow", "allow": "green"}.get(v.action, "white")
        console.print(f"[{color}]{v.action.upper()}[/{color}] [{v.rule_id}] {v.message}")
    for warn in decision.warnings:
        console.print(f"[yellow]WARN:[/yellow] {warn}")

    if decision.outcome == "block":
        raise typer.Exit(1)


@app.command()
def plan(
    state: Optional[Path] = typer.Option(None, "--state"),
    repo_root: Optional[Path] = typer.Option(None, "--repo-root"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    """Build extended plan after observe + policy (MB2 D3)."""
    root = _root(repo_root)
    state_path = state or default_state_path(root)
    snapshot = StateObserver(root, state_path).observe()
    decision = PolicyEngine(root).evaluate(snapshot)

    if decision.outcome == "block":
        console.print("[red]Policy blocked — cannot build plan[/red]")
        raise typer.Exit(1)

    try:
        built = build_plan(snapshot, decision)
    except PlanError as exc:
        console.print(f"[red]Plan failed:[/red] {exc}")
        raise typer.Exit(1) from exc

    if json_out:
        import json

        payload = {
            "epic": built.epic,
            "wave": built.wave,
            "ready_packets": list(built.ready_packets),
            "critical_path": list(built.critical_path),
            "blockers": dict(built.blockers),
            "empty": built.empty,
        }
        console.print_json(json.dumps(payload))
        return

    table = Table(title=f"Plan — {built.epic}")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("wave", str(built.wave))
    table.add_row("ready", ", ".join(built.ready_packets) or "—")
    table.add_row("critical_path", " → ".join(built.critical_path) or "—")
    table.add_row("empty", str(built.empty))
    table.add_row("blockers", str(len(built.blockers)))
    console.print(table)


@app.command()
def cycle(
    state: Optional[Path] = typer.Option(None, "--state"),
    repo_root: Optional[Path] = typer.Option(None, "--repo-root"),
    dry_run: bool = typer.Option(True, "--dry-run/--execute", help="Preflight only (default)"),
) -> None:
    """Run engineering cycle preflight (MB2 D6)."""
    root = _root(repo_root)
    state_path = state or default_state_path(root)
    eng_cycle = EngineeringRuntimeCycle(root, state_path)
    try:
        result = eng_cycle.run_preflight()
    except CycleError as exc:
        console.print(f"[red]Cycle failed:[/red] {exc}")
        raise typer.Exit(1) from exc

    console.print(f"[cyan]Cycle[/cyan] {result.cycle_id}")
    console.print(f"Policy: {result.policy.outcome}")
    if result.plan:
        console.print(
            f"Plan: ready={list(result.plan.ready_packets)} "
            f"path={' → '.join(result.plan.critical_path)} empty={result.plan.empty}"
        )
    if result.policy.outcome == "block":
        raise typer.Exit(1)
    if dry_run:
        console.print("[yellow]Dry run — no schedule/sync executed[/yellow]")


@app.command()
def events(
    tail: int = typer.Option(20, "--tail", "-n"),
    repo_root: Optional[Path] = typer.Option(None, "--repo-root"),
) -> None:
    """Tail build event bus (MB2 D4, read-only)."""
    root = _root(repo_root)
    bus = BuildEventBus(root)
    items = bus.tail(tail)
    if not items:
        console.print("[yellow]No events[/yellow]")
        raise typer.Exit(0)
    table = Table(title=f"Events (last {len(items)})")
    table.add_column("Time")
    table.add_column("Type")
    table.add_column("Payload")
    for ev in items:
        table.add_row(ev.timestamp[:19], ev.type, str(ev.payload)[:80])
    console.print(table)


@app.command("merge-check")
def merge_check(
    repo_root: Optional[Path] = typer.Option(None, "--repo-root"),
) -> None:
    """Merge eligibility stub — always defers to integrator (MB2 D8)."""
    root = _root(repo_root)
    eligibility = merge_eligibility(validation_passed=True)
    console.print(f"Outcome: {eligibility.outcome}")
    console.print(f"Reason: {eligibility.reason}")


@app.command()
def ready(
    state: Optional[Path] = typer.Option(None, "--state"),
    repo_root: Optional[Path] = typer.Option(None, "--repo-root"),
) -> None:
    """List packets ready for dispatch in the current wave."""
    root = _root(repo_root)
    graph = _load(state, root)
    result = validate_graph(graph)
    if not result.ok:
        console.print("[red]Graph invalid — fix lint-graph errors before scheduling[/red]")
        raise typer.Exit(1)

    packets = compute_ready(graph)
    if not packets:
        console.print(
            f"[yellow]No ready packets[/yellow] for wave {graph.wave}. "
            "Run sync or advance wave."
        )
        raise typer.Exit(0)

    table = Table(title=f"Ready packets (wave {graph.wave})")
    table.add_column("ID")
    table.add_column("Agent")
    table.add_column("Owned files")
    for pkt in packets:
        table.add_row(pkt.id, pkt.agent_type, ", ".join(pkt.owned_files) or "—")
    console.print(table)


@app.command()
def schedule(
    state: Optional[Path] = typer.Option(None, "--state"),
    repo_root: Optional[Path] = typer.Option(None, "--repo-root"),
    packet: list[str] = typer.Option(
        None, "--packet", "-p", help="Schedule only these packet ids"
    ),
) -> None:
    """Claim ready packets, set locks, emit dispatch manifest (runtime projection)."""
    root = _root(repo_root)
    state_path = state or default_state_path(root)
    runtime = EngineeringRuntime(root, state_path)
    try:
        result = runtime.schedule(packet_ids=packet or None)
    except EngineeringRuntimeError as exc:
        console.print(f"[red]Schedule failed:[/red] {exc}")
        raise typer.Exit(1) from exc

    console.print(f"[green]Scheduled[/green] {len(result.packet_ids)} packet(s): "
                  f"{', '.join(result.packet_ids)}")
    console.print(f"Manifest: {result.manifest_path}")
    for entry in result.entries:
        console.print(
            f"  {entry['packet_id']} → {entry['suggested_subagent_type']} "
            f"({entry['agent_type']})"
        )


@app.command()
def sync(
    state: Optional[Path] = typer.Option(None, "--state"),
    repo_root: Optional[Path] = typer.Option(None, "--repo-root"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Validate without writing STATE"),
) -> None:
    """Run VALIDATING checks on in_progress packets; advance wave when complete."""
    root = _root(repo_root)
    state_path = state or default_state_path(root)
    runtime = EngineeringRuntime(root, state_path)
    try:
        result = runtime.sync(dry_run=dry_run)
    except EngineeringRuntimeError as exc:
        console.print(f"[red]Sync failed:[/red] {exc}")
        raise typer.Exit(1) from exc

    if result.completed:
        console.print(f"[green]Completed:[/green] {', '.join(result.completed)}")
    if result.failed:
        console.print(f"[red]Blocked:[/red] {', '.join(result.failed)}")
    if result.advanced_to_wave is not None:
        console.print(f"[cyan]Wave advanced to[/cyan] {result.advanced_to_wave}")
    if dry_run:
        console.print("[yellow]Dry run — STATE not written[/yellow]")


@app.command()
def check(
    stage: str = typer.Argument(..., help="Named stage (lint, unit, ci) or shell command"),
    repo_root: Optional[Path] = typer.Option(None, "--repo-root"),
) -> None:
    """Run a validation stage or arbitrary check command."""
    root = _root(repo_root)
    if stage in ("lint", "typecheck", "unit", "unit-frontend", "unit-builder-engine", "drift", "scope", "isolation", "ci", "embed", "search-smoke"):
        result = run_stage(stage, root)
    else:
        from builder_engine.checks import run_shell

        result = run_shell(stage, root)

    if result.ok:
        console.print(f"[green]OK[/green] {result.command}")
        raise typer.Exit(0)
    console.print(f"[red]FAIL[/red] {result.command} (exit {result.exit_code})")
    if result.stderr:
        console.print(result.stderr[-2000:])
    raise typer.Exit(result.exit_code)


if __name__ == "__main__":
    app()
