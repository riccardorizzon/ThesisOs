"""Builder Memory CLI — index, retrieve, snapshot, episodic."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

import json

from builder_memory.context_builder.builder import BuildContextRequest, ContextBuilder
from builder_memory.episodic.store import EpisodicStore
from builder_memory.indexer.indexer import CorpusIndexer
from builder_memory.manifest import Manifest
from builder_memory.paths import find_repo_root, manifest_path
from builder_memory.snapshots.snapshot import SnapshotStore

app = typer.Typer(
    name="builder-memory",
    help="ThesisOS Builder Memory — retrieval-only sidecar for BuilderOS agents (ADR-0019).",
)
console = Console()


def _root(repo_root: Optional[Path]) -> Path:
    return repo_root or find_repo_root()


@app.command()
def index(
    incremental: bool = typer.Option(False, "--incremental", help="Skip unchanged files"),
    repo_root: Optional[Path] = typer.Option(None, "--repo-root", help="ThesisOS repo root"),
) -> None:
    """Index allowlisted corpus paths into BM25 FTS store."""
    root = _root(repo_root)
    stats = CorpusIndexer(root).index(incremental=incremental)
    console.print(
        f"[green]Indexed[/green] {stats.file_count} files, {stats.chunk_count} chunks "
        f"@ {stats.commit_sha[:8]} (skipped {stats.skipped})"
    )


@app.command()
def status(
    repo_root: Optional[Path] = typer.Option(None, "--repo-root"),
) -> None:
    """Show index manifest and staleness."""
    root = _root(repo_root)
    manifest = Manifest.load(manifest_path(root))
    if not manifest:
        console.print("[yellow]No index found. Run: builder-memory index[/yellow]")
        raise typer.Exit(1)

    from builder_memory.indexer.indexer import git_head

    head = git_head(root)
    stale = manifest.is_stale(head)
    table = Table(title="Builder Memory Status")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("commit_sha (index)", manifest.commit_sha[:12])
    table.add_row("commit_sha (HEAD)", head[:12])
    table.add_row("stale", "yes" if stale else "no")
    table.add_row("indexed_at", manifest.indexed_at)
    table.add_row("files", str(manifest.file_count))
    table.add_row("chunks", str(manifest.chunk_count))
    table.add_row("bm25_only", str(manifest.bm25_only))
    console.print(table)
    snapshots = SnapshotStore(root).list_snapshots()
    if snapshots:
        console.print(f"Snapshots: {', '.join(snapshots)}")


@app.command()
def retrieve(
    task: str = typer.Option(..., "--task", "-t", help="Agent task description"),
    role: str = typer.Option("architect", "--role", "-r", help="Agent role"),
    epic: Optional[str] = typer.Option(None, "--epic", help="Epic name (e.g. m2-memory-system)"),
    packet: Optional[str] = typer.Option(None, "--packet", help="Packet id"),
    budget: int = typer.Option(8000, "--budget", help="Token budget"),
    repo_root: Optional[Path] = typer.Option(None, "--repo-root"),
) -> None:
    """Build and print assembled agent context."""
    root = _root(repo_root)
    result = ContextBuilder(root).build(
        BuildContextRequest(
            task=task,
            agent_role=role,
            epic=epic,
            packet_id=packet,
            token_budget=budget,
        )
    )
    if result.index_stale:
        console.print("[yellow]Warning: index is stale vs HEAD. Run: builder-memory index --incremental[/yellow]")
    console.print(result.context.prompt_block)
    if result.context.provenance:
        console.print("\n### Provenance (machine-readable)\n")
        console.print("```yaml")
        console.print(json.dumps([p.to_dict() for p in result.context.provenance], indent=2))
        console.print("```")
    console.print(
        f"\n[dim]~{result.context.token_estimate} tokens · "
        f"{len(result.context.citations)} citations · "
        f"{len(result.context.provenance)} provenance[/dim]"
    )


@app.command("snapshot")
def snapshot_create(
    milestone: str = typer.Option(..., "--milestone", "-m", help="e.g. m1-complete"),
    repo_root: Optional[Path] = typer.Option(None, "--repo-root"),
) -> None:
    """Create a knowledge snapshot manifest at milestone closure."""
    root = _root(repo_root)
    snap = SnapshotStore(root).create(milestone)
    console.print(
        f"[green]Snapshot[/green] `{milestone}` @ {snap.commit_sha[:8]} "
        f"({len(snap.files)} files) → knowledge/snapshots/{milestone}.json"
    )


@app.command("episodic-append")
def episodic_append(
    entry_type: str = typer.Option(..., "--type"),
    summary: str = typer.Option(..., "--summary"),
    ref: list[str] = typer.Option([], "--ref", help="Source path ref (repeatable)"),
    packet: Optional[str] = typer.Option(None, "--packet"),
    repo_root: Optional[Path] = typer.Option(None, "--repo-root"),
) -> None:
    """Append an allowed episodic entry (session memory only)."""
    root = _root(repo_root)
    entry = EpisodicStore(root).append(
        entry_type=entry_type,
        summary=summary,
        source_refs=ref or None,
        packet_id=packet,
    )
    console.print(f"[green]Episodic entry #{entry.id}[/green] [{entry.entry_type}]")


if __name__ == "__main__":
    app()
