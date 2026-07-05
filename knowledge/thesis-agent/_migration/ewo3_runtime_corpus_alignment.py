#!/usr/bin/env python3
"""EWO-3: Runtime Corpus Alignment — idempotent execution via HTTP API."""

from __future__ import annotations

import time
from pathlib import Path

import httpx

BASE = "http://localhost:8000"
TAG = "[kimi-claw-2026-06]"
EWO = "EWO-3"
ROOT = Path(__file__).resolve().parents[1]

MASTERS: tuple[tuple[str, str, str], ...] = (
    ("Bibliography-Master.md", "Bibliography-Master v1.0", "BIBLIOGRAPHY_MASTER"),
    ("Core-Theory-Map.md", "Core-Theory-Map v2.1", "CORE THEORY MAP"),
)

CORPUS_MARKERS: tuple[tuple[str, str], ...] = (
    ("CORPUS-01", "12 autori"),
    ("CORPUS-02", "Mythologies"),
    ("CORPUS-03", "Bourriaud"),
    ("CORPUS-04", "Library-first"),
)

ROLE_MARKERS: tuple[tuple[str, str], ...] = (
    ("Löbach FONDAMENTALE Cap. 1", "Bibliography-Master.md"),
    ("Warburg FONDAMENTALE Cap. 2", "Bibliography-Master.md"),
    ("Benjamin SUPPORTO Cap. 2", "Bibliography-Master.md"),
)

CHAPTER_MARKERS: tuple[tuple[str, str], ...] = (
    ("Löbach processo creativo fasi Cap. 1", "Core-Theory-Map.md"),
    ("Warburg Mnemosyne ricerca visiva Cap. 2", "Core-Theory-Map.md"),
    ("Albers Josef Capitoli tesi Cap. 3 SUPPORTO", "Bibliography-Master.md"),
)


def wait_document(client: httpx.Client, doc_id: str, timeout: float = 300.0) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = client.get(f"{BASE}/documents/{doc_id}")
        r.raise_for_status()
        doc = r.json()
        if doc.get("status") in {"parsed", "indexed", "failed"}:
            return doc
        time.sleep(2)
    raise TimeoutError(doc_id)


def ensure_master(
    client: httpx.Client,
    filename: str,
    title_suffix: str,
    log: list[str],
) -> dict:
    docs = client.get("/documents", params={"limit": 200}).json()
    if isinstance(docs, dict):
        raise RuntimeError(f"documents list failed: {docs}")
    existing = next((d for d in docs if d.get("original_filename") == filename), None)
    if existing is not None:
        log.append(
            f"{filename} skip upload: id={existing['id']} status={existing['status']} "
            f"chunks={existing.get('chunk_count')}"
        )
        return existing

    path = ROOT / "03_PROJECT" / filename
    with path.open("rb") as fh:
        r = client.post(
            "/upload",
            files={"file": (filename, fh, "application/octet-stream")},
            data={
                "title": f"{TAG} {EWO} {title_suffix}",
                "author": "project-master",
            },
        )
    r.raise_for_status()
    doc = wait_document(client, r.json()["id"])
    log.append(
        f"{filename} uploaded: id={doc['id']} status={doc['status']} chunks={doc.get('chunk_count')}"
    )
    return doc


def search_from_file(
    client: httpx.Client,
    query: str,
    filename: str,
    limit: int = 8,
) -> tuple[int, bool]:
    sr = client.post("/search", json={"query": query, "limit": limit})
    if sr.status_code != 200:
        return 0, False
    results = sr.json().get("results") or []
    stem = filename.removesuffix(".md")
    matched = any(
        filename in (x.get("document_title") or "")
        or stem in (x.get("document_title") or "")
        or stem.replace("-", " ") in (x.get("document_title") or "")
        for x in results
    )
    return len(results), matched


def main() -> int:
    log: list[str] = []
    client = httpx.Client(base_url=BASE, timeout=120.0)

    r = client.get("/health")
    r.raise_for_status()
    log.append("health: OK")

    promoted: dict[str, dict] = {}
    for filename, title_suffix, _ in MASTERS:
        promoted[filename] = ensure_master(client, filename, title_suffix, log)

    decisions = client.get("/memory", params={"kind": "decision", "limit": 10}).json()
    dec_row = next((m for m in decisions if m.get("key") == "decisions"), None)
    dec_content = dec_row.get("content", "") if dec_row else ""
    log.append(f"decisions memory: {'present' if dec_row else 'MISSING'} len={len(dec_content)}")

    checks: list[tuple[str, bool, str]] = []
    for filename, _, _ in MASTERS:
        doc = promoted[filename]
        checks.append(
            (
                f"{filename} indexed",
                doc.get("status") == "indexed",
                doc.get("status", ""),
            )
        )
        checks.append(
            (
                f"{filename} chunks",
                (doc.get("chunk_count") or 0) > 0,
                str(doc.get("chunk_count")),
            )
        )

    for marker, needle in CORPUS_MARKERS:
        ok = marker in dec_content and needle.lower() in dec_content.lower()
        checks.append((f"decisions {marker}", ok, needle))

    for query, filename in ROLE_MARKERS:
        n, ok = search_from_file(client, query, filename)
        checks.append((f"role audit {query[:30]}", ok, f"{n} hits"))

    for query, filename in CHAPTER_MARKERS:
        n, ok = search_from_file(client, query, filename)
        checks.append((f"chapter audit {query[:30]}", ok, f"{n} hits"))

    for _, _, search_token in MASTERS:
        filename = next(f for f, _, t in MASTERS if t == search_token)
        n, ok = search_from_file(client, f"{search_token} corpus attivo", filename)
        checks.append((f"retrieval {search_token}", ok, f"{n} hits"))

    failed = [c for c in checks if not c[1]]
    for name, ok, detail in checks:
        log.append(f"  check {name}: {'PASS' if ok else 'FAIL'} ({detail})")

    print("\n".join(log))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
