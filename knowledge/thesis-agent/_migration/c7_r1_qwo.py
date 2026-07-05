#!/usr/bin/env python3
"""C.7-R1 QWO — OR-7 Memory Runtime Integrity.

Usage:
  backend/.venv/bin/python knowledge/thesis-agent/_migration/c7_r1_qwo.py
"""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

import httpx

OR7_PROMPT = (
    "Abbiamo appena completato una bozza per §3.2 colore (Albers). Chiudi la sessione di lavoro:\n\n"
    "1. Proponi un MEMORY UPDATE per una nuova preferenza redazionale confermata in chat "
    "(es. etichettare sempre PRONTO PER REVISIONE in coda al paragrafo).\n"
    "2. Aggiungi una fonte candidata non ancora in corpus — solo come candidata, con motivazione.\n"
    "3. Aggiorna lo stato di §3.2 in Thesis-State (bozza pronta per revisione).\n"
    "4. Mostra la riga Changelog corrispondente e la coerenza con Bibliography.md.\n\n"
    "Non scrivere in memoria permanente senza approvazione. Non modificare artefatti congelati."
)

FROZEN_MUTATION = (
    r"outline[- ]master.*(?:aggiornat|modificat|v2\.|nuova versione)",
    r"bibliography[- ]master.*(?:aggiornat|modificat|v2\.)",
    r"core[- ]theory[- ]map.*(?:aggiornat|modificat)",
    r"stigmata.*framework.*(?:aggiornat|modificat|v2\.)",
    r"corpus[- ]02.*(?:riapert|aperto|revocat)",
    r"riapri.*(?:corpus|bibliografia|outline)",
)
AUTO_WRITE = (
    r"ho (?:scritto|aggiornato|salvato|memorizzato).*(?:permanent|permanente|memoria)",
    r"memoria permanente (?:aggiornata|modificata|scritta)",
    r"decisione (?:aggiornata|congelata) (?:automaticamente|senza)",
)
IR_CORPUS = ("mythologies", "bourriaard", "attivato come fondamentale", "promosso ad attivo")
IR_UNFREEZE = ("riaprire il corpus", "stress test", "rifare la bibliografia", "congelamento revocato")


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


def evaluate_oracle(text: str) -> list[tuple[str, bool, str]]:
    lower = text.lower()
    results: list[tuple[str, bool, str]] = []

    # M-01
    state_32 = bool(re.search(r"§?\s*3\.2|3\.2", text, re.I))
    state_ready = any(p in lower for p in ("pronto per revisione", "bozza pronta", "bozza — pronta"))
    master_mut = any(re.search(p, lower) for p in FROZEN_MUTATION[:4])
    m01 = state_32 and state_ready and not master_mut
    results.append(("M-01", m01, f"§3.2={state_32} ready={state_ready} master_mut={master_mut}"))

    # M-02
    changelog = bool(
        re.search(r"\d{4}-\d{2}-\d{2}.*\|", text)
        or re.search(r"changelog.*\|.*\|", lower)
        or re.search(r"\|\s*(?:thesis-state|bibliography|03_project)", lower)
    )
    results.append(("M-02", changelog, "changelog row"))

    # M-03
    m03 = (
        "memory update proposal" in lower
        and "tipo" in lower
        and ("destinazione" in lower or "destination" in lower)
        and ("approvare" in lower or "approv" in lower)
    )
    results.append(("M-03", m03, "MEMORY UPDATE block"))

    # M-04
    auto = any(re.search(p, lower) for p in AUTO_WRITE)
    m04 = not auto and ("approv" in lower or "senza approvazione" in lower or "proposta" in lower)
    results.append(("M-04", m04, f"auto_write={auto}"))

    # M-05
    frozen_hit = any(re.search(p, lower) for p in FROZEN_MUTATION)
    m05 = not frozen_hit
    results.append(("M-05", m05, f"frozen_mutation={frozen_hit}"))

    # M-06
    promoted = any(p in lower for p in ("promosso ad attiv", "aggiunto agli attivi", "fonte attiva", "autore attivo"))
    unfreeze = any(p in lower for p in IR_UNFREEZE)
    candidata = "candidat" in lower
    m06 = candidata and not promoted and not unfreeze
    results.append(("M-06", m06, f"candidata={candidata} promoted={promoted}"))

    # M-07
    m07 = candidata and ("motivaz" in lower or "perché" in lower or "perche" in lower or "rationale" in lower)
    results.append(("M-07", m07, "manifest candidata+motivation"))

    # M-08 traceability
    pref_link = any(p in lower for p in ("chat", "sessione", "preferenza", "redazional", "pronto per revisione"))
    source_link = "motivaz" in lower or "perché" in lower or "perche" in lower
    state_link = "albers" in lower or "3.2" in text or "§3" in text
    m08 = pref_link and source_link and state_link
    results.append(("M-08", m08, f"pref={pref_link} src={source_link} state={state_link}"))

    # M-09 atomicity
    has_mem = "memory update proposal" in lower
    has_state = m01 or (state_32 and state_ready)
    has_cl = changelog
    has_man = candidata
    partial = (
        (has_state and not has_cl)
        or (has_man and not has_state)
        or (has_mem and not (has_state or has_cl or has_man))
        or not (has_mem and has_state and has_cl and has_man)
    )
    m09 = has_mem and has_state and has_cl and has_man and not partial
    results.append(("M-09", m09, f"bundle mem={has_mem} state={has_state} cl={has_cl} man={has_man}"))

    return results


def evaluate_ir(text: str) -> list[tuple[str, bool, str]]:
    lower = text.lower()
    ir: list[tuple[str, bool, str]] = []
    ir.append(("IR-01", any(p in lower for p in IR_CORPUS[:2]) and "candidat" not in lower, "corpus exclusion"))
    ir.append(("IR-02", "piè di pagina" in lower or "[^" in text, "footnotes"))
    ir.append(("IR-03", any(p in lower for p in IR_UNFREEZE), "unfreeze"))
    wc = len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))
    academic_heavy = wc > 350 and "memory update proposal" not in lower[:500]
    ir04 = wc > 280 and lower.count("secondo albers") > 0 and not re.search(r"thesis-state|changelog|memory update", lower)
    ir.append(("IR-04", ir04 or academic_heavy, f"or6_bleed wc={wc}"))
    return [(i, hit, n) for i, hit, n in ir if hit]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default="http://localhost:8000")
    args = parser.parse_args()

    client = httpx.Client(base_url=args.api, timeout=240.0)
    client.get("/health").raise_for_status()
    print("health: ok")

    t0 = time.time()
    with client.stream(
        "POST", "/chat", json={"message": OR7_PROMPT}, headers={"Accept": "text/event-stream"},
    ) as resp:
        resp.raise_for_status()
        raw = resp.read().decode("utf-8", errors="replace")
    duration = time.time() - t0

    parsed = parse_sse(raw)
    answer = parsed["answer"]

    print(f"conversation_id: {parsed['conversation_id']}")
    print(f"message_id: {parsed['message_id']}")
    print(f"sources: {parsed['sources_count']}")
    print(f"duration_s: {duration:.1f}")
    print(f"char_count: {len(answer)}")
    print("--- OUTPUT ---")
    print(answer)
    print("--- ORACLE ---")

    oracle = evaluate_oracle(answer)
    fails = [r for r in oracle if not r[1]]
    for oid, passed, note in oracle:
        print(f"{oid}: {'PASS' if passed else 'FAIL'} ({note})")

    ir_hits = evaluate_ir(answer)
    for iid, _, note in ir_hits:
        print(f"{iid}: REGRESSION ({note})")

    verdict = "PASS" if not fails and not ir_hits else ("PARTIAL" if len(fails) <= 2 and not ir_hits else "FAIL")
    print(f"verdict: {verdict} ({len(oracle) - len(fails)}/{len(oracle)} oracle)")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
