#!/usr/bin/env python3
"""EWO-7B: Academic Production Path — citation discipline audit + unit gate."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
VENV_PY = BACKEND / ".venv/bin/python"

OR6_PROMPT = (
    "Scrivi un paragrafo di prova per §3.2 colore e Josef Albers in modalità "
    "scrittura accademica. Applica REV-006, separazione A/B, livelli FONDATO/PLAUSIBILE "
    "dove pertinente, firewall persona OFF. Etichetta lo stato del testo."
)


def _run_check_snippet() -> tuple[bool, str]:
    code = """
from app.graph.academic_production import is_academic_writing_query
from app.graph.prompt_wire import render_grounding_prompt
from app.schemas.graph_state import RetrievedChunk

OR6_PROMPT = {prompt!r}
chunk = RetrievedChunk(
    chunk_id="c1", score=0.9, content="Color is relational.",
    document_title="[kimi-claw-2026-06] Albers Interaction of Color", page_from=3,
)
assert is_academic_writing_query(OR6_PROMPT)
prompt = render_grounding_prompt([chunk], academic_writing=True)
assert "author-date" in prompt
assert "Do NOT use numeric bracket citations" in prompt
assert "Albers (1963)" in prompt
print("snippet OK")
""".format(prompt=OR6_PROMPT)
    proc = subprocess.run(
        [str(VENV_PY), "-c", code],
        cwd=BACKEND,
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0, proc.stdout.strip() or proc.stderr[:300]


def main() -> int:
    log: list[str] = []
    checks: list[tuple[str, bool, str]] = []

    ok, detail = _run_check_snippet()
    checks.append(("EWO-7B prompt snippet", ok, detail))

    proc = subprocess.run(
        [str(BACKEND / ".venv/bin/pytest"), "tests/test_academic_production.py", "-q"],
        cwd=BACKEND,
        capture_output=True,
        text=True,
    )
    checks.append(("unit tests academic production", proc.returncode == 0, proc.stdout.strip() or proc.stderr[:200]))
    if proc.returncode != 0:
        log.append(proc.stderr)

    failed = [c for c in checks if not c[1]]
    for name, ok, detail in checks:
        log.append(f"  check {name}: {'PASS' if ok else 'FAIL'} ({detail})")

    print("\n".join(log))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
