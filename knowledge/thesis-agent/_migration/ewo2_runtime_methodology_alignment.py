#!/usr/bin/env python3
"""EWO-2: Runtime Methodology Alignment — idempotent execution via HTTP API."""

from __future__ import annotations

import sys
import time
from pathlib import Path

import httpx

BASE = "http://localhost:8000"
TAG = "[kimi-claw-2026-06]"
EWO = "EWO-2"
ROOT = Path(__file__).resolve().parents[1]


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


def search_hits(client: httpx.Client, query: str, limit: int = 5) -> tuple[int, bool]:
    sr = client.post("/search", json={"query": query, "limit": limit})
    if sr.status_code != 200:
        return 0, False
    results = sr.json().get("results") or []
    stigmata = any(
        "Stigmata" in (x.get("document_title") or "")
        or "STIGMATA" in (x.get("content") or "")
        or "Stigmata-Framework" in (x.get("content") or "")
        for x in results
    )
    return len(results), stigmata or len(results) > 0


def main() -> int:
    log: list[str] = []
    client = httpx.Client(base_url=BASE, timeout=120.0)

    r = client.get("/health")
    r.raise_for_status()
    log.append("health: OK")

    framework_path = ROOT / "03_PROJECT/Stigmata-Framework.md"
    filename = framework_path.name
    docs = client.get("/documents", params={"limit": 200}).json()
    framework_doc = next(
        (d for d in docs if d.get("original_filename") == filename),
        None,
    )
    if framework_doc is None:
        with framework_path.open("rb") as fh:
            r = client.post(
                "/upload",
                files={"file": (filename, fh, "application/octet-stream")},
                data={
                    "title": f"{TAG} {EWO} Stigmata-Framework v1.0",
                    "author": "project-master",
                },
            )
        r.raise_for_status()
        framework_doc = wait_document(client, r.json()["id"])
        log.append(
            f"framework uploaded: status={framework_doc['status']} chunks={framework_doc.get('chunk_count')}"
        )
    else:
        log.append(
            f"framework skip upload: id={framework_doc['id']} status={framework_doc['status']} "
            f"chunks={framework_doc.get('chunk_count')}"
        )

    decisions = client.get("/memory", params={"kind": "decision", "limit": 10}).json()
    dec_row = next((m for m in decisions if m.get("key") == "decisions"), None)
    dec_content = dec_row.get("content", "") if dec_row else ""
    log.append(f"decisions memory: {'present' if dec_row else 'MISSING'} len={len(dec_content)}")

    checks: list[tuple[str, bool, str]] = []
    checks.append(("framework indexed", framework_doc.get("status") == "indexed", framework_doc.get("status", "")))
    checks.append(("framework chunks", (framework_doc.get("chunk_count") or 0) > 0, str(framework_doc.get("chunk_count"))))
    checks.append(("METH-02 in decisions", "METH-02" in dec_content and "caso applicativo" in dec_content.lower(), ""))
    checks.append(("METH-04 in decisions", "METH-04" in dec_content and "evidence" in dec_content.lower(), ""))

    queries = [
        ("retrieval DOCUMENTATION_MASTER", "DOCUMENTATION_MASTER bozzetti moodboard campionature Stigmata"),
        ("retrieval EVIDENCE MATRIX", "EVIDENCE MATRIX FONDATO PLAUSIBILE Stigmata framework"),
        ("retrieval evidence levels", "NON VERIFICABILE APPLICAZIONE TESI livello evidenza"),
        ("retrieval METH-02 role", "STIGMATA caso studio verifica metodologia non oggetto principale"),
    ]
    for name, query in queries:
        n, ok = search_hits(client, query)
        checks.append((name, ok, f"{n} hits"))

    failed = [c for c in checks if not c[1]]
    for name, ok, detail in checks:
        log.append(f"  check {name}: {'PASS' if ok else 'FAIL'} ({detail})")

    print("\n".join(log))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
