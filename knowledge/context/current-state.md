# Current State

> Snapshot as of **2026-06-26**. Branch: `main`. M4 Recovery Sprint closed.

## Where are we?

**M4 Recovery Sprint complete. Product dogfood validated on real Sennett corpus. M5 Tool Router is next active work (product-first); MB2 deferred to ASEP maintenance.**

```text
Constitution (L0–L3 + BS)     ✅ frozen, signed
M4 Retrieval + Recovery       ✅ closed — docs/m4-recovery-final-report.md
M4 pipeline                   🔒 frozen — docs/m4-freeze.md
L4 Phase 0                    ✅ gate closed — docs/l4-phase0-gate.md
L4 MB2 D1 (Observe)           ⏸️ DEFERRED (product-first)
```

## Authorized pipeline

```text
✅ M1–M4 product path usable (chat → memory → ingest → retrieve → grounded answers)
🟢 NEXT (product-first): M5 Tool Router → M6 Writing → continuous dogfood
⏸️ DEFERRED (ASEP maintenance): MB2 Ph1 D1 Observe → Ph2–7 (pull on real block)
```

## M4 recovery summary (2026-06-26)

| Phase | Outcome |
|-------|---------|
| P1 Grounding | `retrieved_context` reaches LLM via `compose_prompt_wire()` |
| P2 Parser | Docling primary in Docker; contracts packaged |
| P3 Embedding | Batched Vertex embed; async failures surfaced |
| P4 Markdown | Native `.md`/`.txt` ingestion |
| P5 Dogfood | End-to-end PASS — `dogfood-m4.md` |

**Regression:** 53 unit tests (`make unit-m4-recovery`) + `make dogfood-m4`.

## What is next?

> **Product-first (provisional trial from 2026-06-25):** ThesisOS = feature acceleration; ASEP = maintenance. See `next-actions.md` → Operating Mode.

1. **M5 — Tool Router** — Critic §12 sign-off on frozen M5 spec, then supervisor/planner/router graph rewire (ADR-0027).
2. **M6 — Writing** — chapter drafting; `m6-complete` = usable thesis product line.
3. **Continuous dogfood** — run `make dogfood-m4` after M5/M6 changes; record bottlenecks in `dogfood-m4.md` or successor.

**Deferred:** MB2 Phase 1 (D1 Observe) — resume only on a real, reproducible product block.
