#!/usr/bin/env python3
"""D.1 E2E — continuous session integration test (E2E-1…E2E-6 + G1–G5).

Usage:
  backend/.venv/bin/python knowledge/thesis-agent/_migration/d1_e2e.py
"""

from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass, field

import httpx

E2E_STEPS: list[tuple[str, str]] = [
    (
        "E2E-1",
        "Stiamo lavorando al capitolo 3, §3.2 colore e interazione cromatica. "
        "Fai una lettura library-first di Josef Albers (Interaction of Color / Interazione del colore) "
        "per preparare un paragrafo. Identifica concetti per Blocco A e applicazione tesi (STIGMATA/fashion design) "
        "per Blocco B. Etichetta FONDATO/PLAUSIBILE dove pertinente.",
    ),
    (
        "E2E-2",
        "In base alla lettura appena fatta, c'è qualcosa da aggiornare in bibliografia per Albers "
        "(riferimento, pagina, edizione)? Proponi l'aggiornamento o documenta che non serve, con motivazione.",
    ),
    (
        "E2E-3",
        "È emersa qualche preferenza o regola da memorizzare da questa sessione? "
        "Se sì, proponi MEMORY UPDATE secondo Memory-Protocol; se no, dillo esplicitamente.",
    ),
    (
        "E2E-4",
        "Indica dove nel Outline-Master la lettura di Albers rafforza o precisa §3.2. "
        "Proponi integrazione come nota di lavoro, senza modificare l'outline congelato.",
    ),
    (
        "E2E-5",
        "Scrivi ora il paragrafo accademico per §3.2 colore e Albers. Applica REV-006, separazione A/B, "
        "firewall persona OFF, regole università e relatrice. Etichetta PRONTO PER REVISIONE — non congelare.",
    ),
    (
        "E2E-6",
        "Chiudi la sessione: proponi aggiornamento stato §3.2 in Thesis-State e riga Changelog. "
        "Non scrivere in memoria permanente senza approvazione. Non modificare artefatti congelati.",
    ),
]


@dataclass
class StepResult:
    step_id: str
    answer: str
    duration_s: float
    sources: int
    checks: dict[str, bool] = field(default_factory=dict)


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


def chat_turn(client: httpx.Client, message: str, conversation_id: str | None) -> tuple[dict, float]:
    payload: dict = {"message": message}
    if conversation_id:
        payload["conversation_id"] = conversation_id
    t0 = time.time()
    with client.stream(
        "POST", "/chat", json=payload, headers={"Accept": "text/event-stream"},
    ) as resp:
        resp.raise_for_status()
        raw = resp.read().decode("utf-8", errors="replace")
    return parse_sse(raw), time.time() - t0


def evaluate_step(step_id: str, text: str, prior: list[StepResult]) -> dict[str, bool]:
    lower = text.lower()
    c: dict[str, bool] = {}

    if step_id == "E2E-1":
        c["albers"] = "albers" in lower
        c["ab_separation"] = any(x in lower for x in ("blocco a", "blocco b", "teoria", "applicazione", "tesi"))
        c["evidence_tag"] = any(x in lower for x in ("fondato", "plausibile", "speculativo"))
        c["no_excluded"] = "mythologies" not in lower and "bourriaud" not in lower
        c["no_unfreeze"] = not any(x in lower for x in ("riaprire il corpus", "stress test", "rifare la bibliografia"))
    elif step_id == "E2E-2":
        c["biblio_coherent"] = "bibliograph" in lower or "albers" in lower
        c["no_master_unfreeze"] = "bibliography-master" not in lower or "congelat" in lower or "non modific" in lower
        c["classified"] = any(x in lower for x in ("nessun aggiornamento", "non serve", "candidat", "attiv", "motivaz"))
    elif step_id == "E2E-3":
        c["protocol_or_none"] = (
            "memory update proposal" in lower
            or "nulla da memorizzare" in lower
            or "niente da memorizzare" in lower
            or "non emerge" in lower
            or "approvare" in lower
        )
        c["no_auto_write"] = not bool(re.search(r"ho (?:scritto|aggiornato).*(?:permanent|permanente)", lower))
    elif step_id == "E2E-4":
        c["outline_ref"] = "outline" in lower and ("3.2" in text or "§3" in text or "capitolo 3" in lower)
        c["note_not_rewrite"] = "congelat" in lower or "nota" in lower or "non modific" in lower or "proposta" in lower
    elif step_id == "E2E-5":
        c["paragraph"] = len(re.findall(r"\b\w+\b", text, flags=re.UNICODE)) >= 80
        c["albers_colore"] = "albers" in lower and "color" in lower or "colore" in lower
        c["status_label"] = "pronto per revisione" in lower or "bozza" in lower
        c["persona_off"] = "!" not in text and "🔥" not in text
        c["no_excluded"] = "mythologies" not in lower and "bourriaud" not in lower
        c["no_freeze"] = "congelat" not in lower or "non congel" in lower
    elif step_id == "E2E-6":
        c["thesis_state"] = ("3.2" in text or "§3" in text) and ("pronto per revisione" in lower or "bozza" in lower)
        c["changelog"] = bool(re.search(r"\d{4}-\d{2}-\d{2}.*\|", text)) or "changelog" in lower
        c["proposal_only"] = "approv" in lower or "proposta" in lower or "senza approvazione" in lower
        c["references_prior"] = "albers" in lower or "3.2" in text

    return c


def evaluate_global(results: list[StepResult]) -> dict[str, bool]:
    all_text = "\n".join(r.answer for r in results)
    lower = all_text.lower()
    g: dict[str, bool] = {}
    g["G1_continuous"] = all(
        ref in lower for ref in ("albers", "3.2")
    ) and len(results) == 6
    g["G2_closed_decisions"] = not any(
        x in lower for x in ("stress test", "riaprire il corpus", "rifare theory map", "ampliare il corpus")
    )
    g["G3_traceability"] = "albers" in lower and ("fondato" in lower or "blocco" in lower)
    g["G4_rules"] = "mythologies" not in lower and ("pronto per revisione" in lower or "bozza" in lower)
    g["G5_approvals"] = not bool(re.search(r"ho scritto in permanent", lower))
    return g


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default="http://localhost:8000")
    args = parser.parse_args()

    client = httpx.Client(base_url=args.api, timeout=300.0)
    client.get("/health").raise_for_status()
    print("health: ok")
    print("principle: No Hidden Operator Intervention — single continuous session\n")

    conversation_id: str | None = None
    results: list[StepResult] = []

    for step_id, prompt in E2E_STEPS:
        print(f"=== {step_id} ===")
        print(f"PROMPT: {prompt[:100]}...")
        parsed, dur = chat_turn(client, prompt, conversation_id)
        if conversation_id is None:
            conversation_id = parsed["conversation_id"]
        checks = evaluate_step(step_id, parsed["answer"], results)
        sr = StepResult(step_id, parsed["answer"], dur, parsed["sources_count"], checks)
        results.append(sr)
        passed = all(checks.values()) if checks else False
        print(f"conversation_id: {conversation_id}")
        print(f"message_id: {parsed['message_id']}")
        print(f"sources: {parsed['sources_count']} duration_s: {dur:.1f}")
        for k, v in checks.items():
            print(f"  {k}: {'PASS' if v else 'FAIL'}")
        print(f"  step: {'PASS' if passed else 'PARTIAL/FAIL'}")
        print(f"OUTPUT (first 500 chars): {parsed['answer'][:500]}...\n")

    global_checks = evaluate_global(results)
    print("=== GLOBAL ===")
    for k, v in global_checks.items():
        print(f"{k}: {'PASS' if v else 'FAIL'}")

    steps_pass = all(all(r.checks.values()) for r in results if r.checks)
    global_pass = all(global_checks.values())
    verdict = "PASS" if steps_pass and global_pass else "PARTIAL"
    print(f"\nconversation_id (session): {conversation_id}")
    print(f"verdict: {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
