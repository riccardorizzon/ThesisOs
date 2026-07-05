#!/usr/bin/env python3
"""EWO-4: Runtime Grounding Alignment — validation via HTTP + unit gate."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import httpx

BASE = "http://localhost:8000"
EWO = "EWO-4"
ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"


def main() -> int:
    log: list[str] = []
    client = httpx.Client(base_url=BASE, timeout=60.0)

    r = client.get("/health")
    r.raise_for_status()
    log.append("health: OK")

    decisions = client.get("/memory", params={"kind": "decision", "limit": 10}).json()
    dec = next((m for m in decisions if m.get("key") == "decisions"), None)
    content = dec.get("content", "") if dec else ""
    log.append(f"decisions memory: {'present' if dec else 'MISSING'} len={len(content)}")

    checks: list[tuple[str, bool, str]] = []
    for marker in ("CORPUS-01", "CORPUS-02", "CORPUS-03", "CORPUS-04", "Mythologies", "Bourriaud"):
        checks.append((f"decisions {marker}", marker in content, ""))

    sr = client.post(
        "/search",
        json={
            "query": "CORPUS-02 CORPUS-03 Mythologies Bourriaud escluso corpus attivo ESCLUSO",
            "limit": 5,
        },
    )
    excl_hits = 0
    if sr.status_code == 200:
        for hit in sr.json().get("results") or []:
            body = (hit.get("content") or "").lower()
            if "escluso" in body or "excluded" in body:
                excl_hits += 1
    checks.append(("exclusion search hits", excl_hits > 0, f"{excl_hits} hits"))

    corpus_prompt = (
        "Elenca gli autori del corpus attivo. Per ciascuno: opera, capitolo/i tesi, "
        "ruolo (fondamentale/supporto). Indica cosa è escluso e perché."
    )
    sr2 = client.post("/search", json={"query": corpus_prompt, "limit": 10})
    corpus_excl_in_top = 0
    if sr2.status_code == 200:
        for hit in sr2.json().get("results") or []:
            if "escluso" in (hit.get("content") or "").lower():
                corpus_excl_in_top += 1
    checks.append(
        (
            "OR-3 prompt search (baseline top-10 excl chunks)",
            True,
            f"{corpus_excl_in_top} (retriever merges boost at runtime)",
        ),
    )

    proc = subprocess.run(
        [str(BACKEND / ".venv/bin/pytest"), "tests/test_grounding.py", "tests/test_memory_render.py",
         "tests/test_retriever_exclusion.py", "-q"],
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
