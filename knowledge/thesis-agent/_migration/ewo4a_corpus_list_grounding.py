#!/usr/bin/env python3
"""EWO-4A: Corpus-list Grounding Remediation — OR-3 retrieval audit + unit gate."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import httpx

BASE = "http://localhost:8000"
ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"

OR3_PROMPT = (
    "Elenca gli autori del corpus attivo. Per ciascuno: opera, capitolo/i tesi, "
    "ruolo (fondamentale/supporto). Indica cosa è escluso e perché."
)

# Mirror retriever merge (must stay aligned with backend/app/graph/retriever.py)
sys.path.insert(0, str(ROOT / "backend"))
from app.graph.corpus_query import (  # noqa: E402
    CORPUS_LIST_BOOST_QUERY,
    EXCLUSION_BOOST_QUERY,
)
from app.graph.retriever import _merge_results  # noqa: E402
from app.schemas.retrieval import SearchResultItem  # noqa: E402


def _to_items(raw: list[dict]) -> list[SearchResultItem]:
    out: list[SearchResultItem] = []
    for hit in raw:
        out.append(
            SearchResultItem(
                chunk_id=hit["chunk_id"],
                document_id=hit.get("document_id", ""),
                chunk_hash=hit.get("chunk_hash", ""),
                score=float(hit.get("score") or 0),
                content=hit.get("content") or "",
                document_title=hit.get("document_title"),
                page_from=hit.get("page_from"),
                page_to=hit.get("page_to"),
            )
        )
    return out


def main() -> int:
    log: list[str] = []
    client = httpx.Client(base_url=BASE, timeout=60.0)

    r = client.get("/health")
    r.raise_for_status()
    log.append("health: OK")

    checks: list[tuple[str, bool, str]] = []

    primary = _to_items(client.post("/search", json={"query": OR3_PROMPT, "limit": 12}).json().get("results") or [])
    exclusion = _to_items(
        client.post("/search", json={"query": EXCLUSION_BOOST_QUERY, "limit": 4}).json().get("results") or []
    )
    corpus = _to_items(
        client.post("/search", json={"query": CORPUS_LIST_BOOST_QUERY, "limit": 6}).json().get("results") or []
    )
    merged = _merge_results(primary, exclusion, corpus, limit=12)

    titles = [m.document_title or "" for m in merged]
    bodies = " ".join(m.content for m in merged)
    bib_hits = sum(1 for t in titles if "Bibliography-Master" in t)
    has_eco = "Eco" in bodies
    has_flugel = "Flügel" in bodies or "Flugel" in bodies
    has_excl = "escluso" in bodies.lower() or "ESCLUSO" in bodies
    bodies_lower = bodies.lower()
    has_a_sections = (
        any(token in bodies_lower for token in ("fondamentale", "fondamentali"))
        and "supporto" in bodies_lower
    )

    checks.append(("Bibliography-Master in merged top-12", bib_hits >= 1, f"{bib_hits} chunks"))
    checks.append(("Eco in merged context", has_eco, ""))
    checks.append(("Flügel in merged context", has_flugel, ""))
    checks.append(("exclusion markers in merged context", has_excl, ""))
    checks.append(("FOND/SUPPORTO sections in merged context", has_a_sections, ""))

    proc = subprocess.run(
        [
            str(BACKEND / ".venv/bin/pytest"),
            "tests/test_grounding.py",
            "tests/test_memory_render.py",
            "tests/test_retriever_exclusion.py",
            "-q",
        ],
        cwd=BACKEND,
        capture_output=True,
        text=True,
    )
    checks.append(("unit tests grounding", proc.returncode == 0, proc.stdout.strip() or proc.stderr[:200]))
    if proc.returncode != 0:
        log.append(proc.stderr)

    failed = [c for c in checks if not c[1]]
    for name, ok, detail in checks:
        log.append(f"  check {name}: {'PASS' if ok else 'FAIL'} ({detail})")

    print("\n".join(log))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
