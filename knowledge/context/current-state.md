# Current State

> Snapshot as of **2026-06-28**. Branch: `main`. Pre-M5 Closure Sprint complete.

## Where are we?

**M4 Recovery closed and frozen. MB2 Engineering Runtime closed. Pre-M5 gates passed — M5 Tool Router authorized to start.**

```text
Constitution (L0–L3 + BS)     ✅ frozen, signed
M4 Retrieval + Recovery       ✅ closed — docs/m4-recovery-final-report.md
M4 pipeline                   🔒 frozen — docs/m4-freeze.md
L4 Phase 0                    ✅ gate closed — docs/l4-phase0-gate.md
L4 MB2 (D1–D10)               ✅ closed — docs/mb2-phase-gate.md (2026-06-28)
M5 spec + ADR-0027            ✅ Critic sign-off — docs/m5-critic-signoff.md (2026-06-28)
Pre-M5 Closure                ✅ CI green, isolated test DB, regression PASS
```

## Authorized pipeline

```text
✅ M1–M4 product path usable (chat → memory → ingest → retrieve → grounded answers)
✅ ASEP MB2 Engineering Runtime loop (observe→policy→plan→cycle→schedule→sync→events)
🟢 NEXT (product-first): M5 Tool Router → M6 Writing → continuous dogfood
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

1. **M5 — Tool Router** — implement supervisor/planner/router graph rewire per ADR-0027 (`plans/m5-tool-router-plan.md` Phase 1).
2. **M6 — Writing** — chapter drafting; `m6-complete` = usable thesis product line.
3. **Continuous dogfood** — run `make dogfood-m4` after M5/M6 changes; record bottlenecks in `dogfood-m4.md` or successor.

**ASEP:** MB2 closed; maintenance mode per Operating Mode in `next-actions.md`.
