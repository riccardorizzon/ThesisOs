"""Prompt assembly with NON-AUTHORITATIVE header and citations."""

from __future__ import annotations

from dataclasses import dataclass

from builder_memory.rankers.base import RetrievalProvenance
from builder_memory.retriever.retriever import RetrievedChunk


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


@dataclass(frozen=True)
class AssembledContext:
    prompt_block: str
    citations: list[dict[str, str | float]]
    provenance: list[RetrievalProvenance]
    token_estimate: int


def assemble_prompt(
    *,
    task: str,
    chunks: list[RetrievedChunk],
    commit_sha: str,
    token_budget: int = 8000,
    episodic_hints: list[str] | None = None,
    snapshot_note: str | None = None,
    provenance: list[RetrievalProvenance] | None = None,
) -> AssembledContext:
    """Build compressed execution context for agent prompts."""
    header = (
        "## Builder Context (NON-AUTHORITATIVE — verify in repository)\n\n"
        f"> Indexed at commit `{commit_sha}`. **Filesystem wins on conflict.**\n"
    )
    if snapshot_note:
        header += f"> {snapshot_note}\n"

    sections: list[str] = [header]
    citations: list[dict[str, str | float]] = []
    used_tokens = estimate_tokens(header)

    def add_section(
        title: str,
        body: str,
        source: str,
        *,
        score: float | None = None,
        source_type: str | None = None,
    ) -> bool:
        nonlocal used_tokens
        block = f"\n### {title}\n{body}\n\n*Source: `{source}`*"
        if score is not None and source_type is not None:
            block += f" · score={score:.2f} · type={source_type}"
        block += "\n"
        cost = estimate_tokens(block)
        if used_tokens + cost > token_budget:
            return False
        sections.append(block)
        citation: dict[str, str | float] = {"path": source, "title": title}
        if score is not None:
            citation["score"] = score
        if source_type is not None:
            citation["source_type"] = source_type
        citations.append(citation)
        used_tokens += cost
        return True

    provenance_by_path = {p.path: p for p in (provenance or [])}

    # Group chunks by kind for readability.
    by_kind: dict[str, list[RetrievedChunk]] = {}
    for chunk in chunks:
        by_kind.setdefault(chunk.kind, []).append(chunk)

    kind_titles = {
        "state": "Orchestration state",
        "knowledge": "Project knowledge",
        "adr": "Relevant ADRs",
        "contract": "Relevant contracts",
        "spec": "Milestone specification",
        "plan": "Plans",
        "promotion": "Promotion evidence",
        "decision": "Decisions",
        "doc": "Documentation",
        "research": "Research",
        "snapshot": "Milestone snapshot",
    }

    for kind in (
        "state",
        "knowledge",
        "adr",
        "contract",
        "spec",
        "plan",
        "promotion",
        "decision",
        "doc",
        "research",
        "snapshot",
    ):
        for chunk in by_kind.get(kind, []):
            excerpt = chunk.content
            max_chars = min(2000, (token_budget - used_tokens) * 4)
            if max_chars < 100:
                break
            if len(excerpt) > max_chars:
                excerpt = excerpt[:max_chars] + "\n…"
            title = kind_titles.get(kind, kind)
            if chunk.title and chunk.title not in title:
                title = f"{title}: {chunk.title}"
            prov = provenance_by_path.get(chunk.source_path)
            if not add_section(
                title,
                excerpt,
                chunk.source_path,
                score=prov.score if prov else None,
                source_type=prov.source_type if prov else chunk.kind,
            ):
                break

    if provenance:
        prov_lines = "\n".join(
            f"- path: {p.path}\n  score: {p.score:.2f}\n  source_type: {p.source_type}"
            for p in provenance
        )
        add_section(
            "Retrieval provenance (for Critic)",
            prov_lines,
            ".builder-memory/index.sqlite",
            score=1.0,
            source_type="provenance",
        )

    if episodic_hints:
        body = "\n".join(f"- {h}" for h in episodic_hints[:5])
        add_section(
            "Episodic hints (session memory — NON-AUTHORITATIVE)",
            body,
            ".builder-memory/episodic.sqlite",
        )

    sections.append(f"\n---\n## Your task\n{task}\n")
    prompt = "".join(sections)
    return AssembledContext(
        prompt_block=prompt,
        citations=citations,
        provenance=provenance or [],
        token_estimate=estimate_tokens(prompt),
    )
