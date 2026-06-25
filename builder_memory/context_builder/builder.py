"""Context Builder — orchestrates retrieval for a builder agent task."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from builder_memory.rankers.bm25 import Bm25Ranker
from builder_memory.rankers.base import RetrievalProvenance
from builder_memory.context_builder.assembly import AssembledContext, assemble_prompt
from builder_memory.episodic.store import EpisodicStore
from builder_memory.indexer.indexer import git_head
from builder_memory.manifest import Manifest
from builder_memory.paths import manifest_path
from builder_memory.retriever.retriever import Retriever, RetrievedChunk
from builder_memory.snapshots.snapshot import SnapshotStore, diff_since_snapshot


@dataclass(frozen=True)
class BuildContextRequest:
    task: str
    agent_role: str = "architect"
    epic: str | None = None
    packet_id: str | None = None
    token_budget: int = 8000
    include_episodic: bool = True


@dataclass(frozen=True)
class BuildContextResult:
    context: AssembledContext
    commit_sha: str
    index_stale: bool
    changed_since_snapshot: list[str]


class ContextBuilder:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.retriever = Retriever(repo_root)
        self.episodic = EpisodicStore(repo_root)
        self.snapshots = SnapshotStore(repo_root)
        self.ranker = Bm25Ranker()

    def build(self, request: BuildContextRequest) -> BuildContextResult:
        manifest = Manifest.load(manifest_path(self.repo_root))
        commit_sha = git_head(self.repo_root)
        index_stale = manifest.is_stale(commit_sha) if manifest else True

        chunks: list[RetrievedChunk] = []
        seen: set[str] = set()

        def add(chunk: RetrievedChunk) -> None:
            if chunk.source_path not in seen:
                seen.add(chunk.source_path)
                chunks.append(chunk)

        # Mandatory injections first.
        for chunk in self.retriever.mandatory_chunks():
            add(chunk)

        # Epic-specific spec injection.
        if request.epic:
            spec_glob = list(
                (self.repo_root / "docs/superpowers/specs").glob(f"*{request.epic}*")
            )
            for spec_path in spec_glob[:1]:
                rel = spec_path.relative_to(self.repo_root).as_posix()
                for chunk in self.retriever.fetch_by_path(rel):
                    add(chunk)

        # Task-driven BM25 retrieval.
        query = request.task
        if request.packet_id:
            query = f"{query} {request.packet_id}"
        for chunk in self.retriever.retrieve(
            query, agent_role=request.agent_role, limit=10
        ):
            add(chunk)

        ranked = self.ranker.rank(chunks, agent_role=request.agent_role)
        provenance = self.ranker.provenance(chunks, agent_role=request.agent_role)

        # Episodic hints.
        episodic_hints: list[str] = []
        if request.include_episodic:
            for entry in self.episodic.recent(limit=5):
                episodic_hints.append(f"[{entry.entry_type}] {entry.summary}")

        # Snapshot diff note.
        changed: list[str] = []
        snapshot_note: str | None = None
        latest = self.snapshots.latest_snapshot()
        if latest:
            changed = diff_since_snapshot(self.repo_root, latest)
            if changed:
                snapshot_note = (
                    f"Since snapshot `{latest.milestone}`: "
                    f"{len(changed)} indexed file(s) changed."
                )

        context = assemble_prompt(
            task=request.task,
            chunks=ranked,
            commit_sha=commit_sha,
            token_budget=request.token_budget,
            episodic_hints=episodic_hints or None,
            snapshot_note=snapshot_note,
            provenance=provenance,
        )
        return BuildContextResult(
            context=context,
            commit_sha=commit_sha,
            index_stale=index_stale,
            changed_since_snapshot=changed,
        )
