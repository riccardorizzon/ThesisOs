"""Build Workflow Engine CLI (MB1 Phase 1: lint-graph, status, ready)."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from builder_engine.graph import BuilderGraph
from builder_engine.paths import default_state_path, find_repo_root
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


if __name__ == "__main__":
    app()
