#!/usr/bin/env python3
"""C.6-R3 QWO — OR-6 final requalification (post-EWO-7C).

Usage:
  backend/.venv/bin/python knowledge/thesis-agent/_migration/c6_r3_qwo.py
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
VENV_PY = BACKEND / ".venv/bin/python"

OR6_PROMPT = (
    "Scrivi un paragrafo di prova per §3.2 colore e Josef Albers in modalità "
    "scrittura accademica. Applica REV-006, separazione A/B, livelli FONDATO/PLAUSIBILE "
    "dove pertinente, firewall persona OFF. Etichetta lo stato del testo."
)

PERSONA_BLOCKLIST = (
    "let's go", "we move", "okay, good", "boss fight", "recovery mode",
    "🔥", "⚡", "💥", "🫡", "🎯", "🏁",
)
ITALIAN_TOKENS = (" di ", " che ", " nel ", " della ", " come ")


def verify_enforcement_path() -> tuple[bool, str]:
    code = f"""
from app.graph.academic_production import (
    is_academic_writing_query,
    needs_citation_enforcement_retry,
    ACADEMIC_INFERENCE_ENFORCEMENT,
)
from app.graph.prompt_wire import compose_prompt_wire
from app.schemas.graph_state import GraphState, Message, RetrievedChunk

prompt = {OR6_PROMPT!r}
assert is_academic_writing_query(prompt)
state = GraphState(
    messages=[Message(role="user", content=prompt)],
    retrieved_context=[
        RetrievedChunk(
            chunk_id="c1", score=0.9, content="x",
            document_title="[kimi-claw-2026-06] Albers Interaction of Color", page_from=3,
        )
    ],
)
system = compose_prompt_wire(state)[0].content
assert "numbered sources" not in system.lower()
assert "Example of correct citation format" in system
assert ACADEMIC_INFERENCE_ENFORCEMENT.split()[0] in system
assert "Do NOT use numeric bracket citations" in system
assert needs_citation_enforcement_retry("testo con citazione [2] senza autore-data")
assert not needs_citation_enforcement_retry("Secondo Albers (Albers, 1963) ok.")
print("ewo7c_path_ok")
"""
    proc = subprocess.run([str(VENV_PY), "-c", code], cwd=BACKEND, capture_output=True, text=True)
    return proc.returncode == 0, proc.stdout.strip() or proc.stderr[:500]


def parse_sse(raw: str) -> dict:
    parsed: dict = {"conversation_id": None, "message_id": None, "sources_count": 0, "tokens": []}
    for block in raw.replace("\r\n", "\n").split("\n\n"):
        lines = [line for line in block.strip().split("\n") if line]
        if len(lines) < 2:
            continue
        event = lines[0].split(":", 1)[1].strip()
        data = json.loads(lines[1][6:])
        if event == "done":
            parsed["conversation_id"] = data.get("conversation_id")
            parsed["message_id"] = data.get("message_id")
        elif event == "sources":
            parsed["sources_count"] = len(data.get("sources", []))
        elif event == "token":
            parsed["tokens"].append(data.get("text", ""))
    parsed["answer"] = "".join(parsed["tokens"])
    return parsed


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))


def evaluate_oracle(text: str) -> list[tuple[str, bool, str]]:
    lower = text.lower()
    results: list[tuple[str, bool, str]] = []

    wc = word_count(text)
    results.append(("W-01", wc >= 80 and ("albers" in lower or "colore" in lower), f"{wc} words"))

    w02 = "!" not in text and not any(b in lower for b in PERSONA_BLOCKLIST)
    results.append(("W-02", w02, "persona OFF"))

    theory = any(c in lower for c in ("secondo albers", "albers sostiene", "blocco a"))
    application = any(c in lower for c in ("nella tesi", "applicazione", "blocco b", "stigmata", "caso studio", "fashion design"))
    results.append(("W-03", theory and application, f"theory={theory} application={application}"))

    w04 = bool(re.search(r"\(Albers,", text, re.I) or "secondo albers" in lower
               or any(t in lower for t in ("fondato", "plausibile", "speculativo")))
    results.append(("W-04", w04, "attribution marker"))

    w05 = any(t in lower for t in ("fondato", "plausibile", "speculativo"))
    results.append(("W-05", w05, "evidence tag"))

    w06 = bool(re.search(r"\(Albers,\s*\d{{4}}\)", text, re.I)) or bool(
        re.search(r"Albers\s*\(\s*\d{{4}}\s*\)", text, re.I)
    )
    results.append(("W-06", w06, "autore-date"))

    w07 = not any(m in lower for m in ("piè di pagina", "nota a piè")) and "[^" not in text
    results.append(("W-07", w07, "no footnotes"))

    w08 = "bozza" in lower or "pronto per revisione" in lower
    results.append(("W-08", w08, "status label"))

    w09 = not re.search(r"\bcongelat[oa]\b", lower)
    results.append(("W-09", w09, "no unilateral freeze"))

    w10 = "mythologies" not in lower and "bourriaud" not in lower
    results.append(("W-10", w10, "excluded authors absent"))

    w11 = bool(re.search(r"\[\d+\]", text)) or "interaction of color" in lower or "interazione del colore" in lower
    results.append(("W-11", w11, "source anchor"))

    italian_hits = sum(1 for tok in ITALIAN_TOKENS if tok in lower)
    results.append(("W-12", italian_hits >= 3 and w02, f"italian tokens={italian_hits}"))

    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default="http://localhost:8000")
    args = parser.parse_args()

    ok, detail = verify_enforcement_path()
    print(f"ewo7c_path: {'PASS' if ok else 'FAIL'} ({detail})")
    if not ok:
        return 1

    client = httpx.Client(base_url=args.api, timeout=240.0)
    client.get("/health").raise_for_status()
    print("health: ok")

    t0 = time.time()
    with client.stream(
        "POST", "/chat", json={"message": OR6_PROMPT}, headers={"Accept": "text/event-stream"},
    ) as resp:
        resp.raise_for_status()
        raw = resp.read().decode("utf-8", errors="replace")
    duration = time.time() - t0

    parsed = parse_sse(raw)
    answer = parsed["answer"]
    numeric = bool(re.search(r"\[\d+\]", answer))
    author_date = bool(re.search(r"\(Albers,\s*\d{4}\)", answer, re.I))

    print(f"conversation_id: {parsed['conversation_id']}")
    print(f"message_id: {parsed['message_id']}")
    print(f"sources: {parsed['sources_count']}")
    print(f"duration_s: {duration:.1f}")
    print(f"word_count: {word_count(answer)}")
    print(f"output_has_numeric: {numeric}")
    print(f"output_has_author_date: {author_date}")
    print("--- OUTPUT ---")
    print(answer)
    print("--- ORACLE ---")

    oracle = evaluate_oracle(answer)
    fails = [r for r in oracle if not r[1]]
    for wid, passed, note in oracle:
        print(f"{wid}: {'PASS' if passed else 'FAIL'} ({note})")

    if fails and ok and numeric and not author_date:
        print("failure_class: Model Non-Compliance (EWO-7C path verified)")

    verdict = "PASS" if not fails else ("PARTIAL" if len(fails) == 1 and fails[0][0] == "W-06" else "FAIL")
    print(f"verdict: {verdict} ({len(oracle) - len(fails)}/{len(oracle)} oracle)")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
