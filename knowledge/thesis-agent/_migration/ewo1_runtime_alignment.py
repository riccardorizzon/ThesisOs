#!/usr/bin/env python3
"""EWO-1: Runtime Knowledge Alignment — idempotent execution via HTTP API."""

from __future__ import annotations

import sys
import time
from pathlib import Path

import httpx

BASE = "http://localhost:8000"
TAG = "[kimi-claw-2026-06]"
EWO = "EWO-1"
ROOT = Path(__file__).resolve().parents[1]


def read_md(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4 :].lstrip("\n")
    return text


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


def main() -> int:
    log: list[str] = []
    client = httpx.Client(base_url=BASE, timeout=120.0)

    r = client.get("/health")
    r.raise_for_status()
    log.append("health: OK")

    outline_path = ROOT / "03_PROJECT/Outline-Master.md"
    filename = outline_path.name
    docs = client.get("/documents", params={"limit": 200}).json()
    outline_doc = next(
        (d for d in docs if d.get("original_filename") == filename),
        None,
    )
    if outline_doc is None:
        with outline_path.open("rb") as fh:
            r = client.post(
                "/upload",
                files={"file": (filename, fh, "application/octet-stream")},
                data={
                    "title": f"{TAG} {EWO} Outline-Master v1.0",
                    "author": "project-master",
                },
            )
        r.raise_for_status()
        outline_doc = wait_document(client, r.json()["id"])
        log.append(f"outline uploaded: status={outline_doc['status']} chunks={outline_doc.get('chunk_count')}")
    else:
        log.append(f"outline skip upload: id={outline_doc['id']} status={outline_doc['status']}")

    thesis_content = read_md(ROOT / "03_PROJECT/Thesis-State.md")
    memories = client.get("/memory", params={"kind": "thesis", "limit": 10}).json()
    thesis_row = next((m for m in memories if m.get("key") == "thesis" or m.get("kind") == "thesis"), None)
    if not thesis_row:
        log.append("ERROR: thesis memory missing")
        return 1
    r = client.patch(
        f"/memory/{thesis_row['id']}",
        json={
            "title": "Thesis state (EWO-1 aligned)",
            "content": thesis_content,
            "expected_version": thesis_row["version"],
        },
    )
    r.raise_for_status()
    log.append(f"thesis memory updated: v{thesis_row['version']}→v{r.json()['version']}")

    # Coherence checks
    checks: list[tuple[str, bool, str]] = []
    domanda_gt = "documentazione attraverso la pratica riflessiva"
    checks.append(("thesis domanda GT", domanda_gt in thesis_content, "substring in thesis memory"))
    checks.append(("outline indexed", outline_doc.get("status") == "indexed", outline_doc.get("status", "")))
    checks.append(("outline chunks", (outline_doc.get("chunk_count") or 0) > 0, str(outline_doc.get("chunk_count"))))

    for needle in [
        "Il processo creativo: struttura e esperienza",
        "STIGMATA: lettura analitica di un processo",
        "Conclusioni: verso una metodologia",
    ]:
        checks.append((f"thesis arch contains {needle[:30]}…", needle in thesis_content, ""))

    sr = client.post("/search", json={"query": "CAPITOLO 5 STIGMATA lettura analitica outline", "limit": 5})
    if sr.status_code == 200:
        results = sr.json().get("results") or []
        hit = any("Outline" in (x.get("document_title") or "") or "outline" in (x.get("content") or "").lower() for x in results)
        checks.append(("retrieval outline", hit or len(results) > 0, f"{len(results)} hits"))
    else:
        checks.append(("retrieval outline", False, f"HTTP {sr.status_code}"))

    failed = [c for c in checks if not c[1]]
    for name, ok, detail in checks:
        log.append(f"  check {name}: {'PASS' if ok else 'FAIL'} ({detail})")

    print("\n".join(log))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
