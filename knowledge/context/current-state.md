# Current State

> Snapshot as of **2026-06-25**. Branch: `main`. Tag: `l4-phase0-complete`.

## Where are we?

**L4 Phase 0 gate closed. Baseline committed. MB2 Phase 1 (D1 — Observe) authorized.**

```text
Constitution (L0–L3 + BS)     ✅ frozen, signed
DR-001 + ETM v1.1             ✅ approved
MB2 spec rebase               ✅ Architect Approved §13
L4 Phase 0 (l2 plan Ph1–2)    ✅ gate closed — docs/l4-phase0-gate.md
L4 MB2 D1 (Observe)           🟢 authorized — not started
```

## Authorized pipeline

```text
✅ Constitution → MB2 spec → L4 Phase 0 → Gate → Baseline
🟢 MB2 Phase 1 — D1 Observe (plans/mb2-adaptive-runtime-plan.md Ph1)
⏸️ MB2 Ph2–7 — sequential per plan
```

## Phase 0 baseline (committed)

| Module | Purpose |
|--------|---------|
| `builder_engine/gsm_task.py` | T-01–T-12 + INV-A1–A5 |
| `builder_engine/gsm.py` | `GlobalStateMachine` wrapper |
| `builder_engine/invariants.py` | Class B pre-commit pass |
| `builder_engine/state_io.py` | Invariant hook on `save_raw_state` |
| `builder_engine/runtime.py` | GSM-aligned schedule/sync |

**Rollback baseline:** `f117d3d`  
**Gate record:** `docs/l4-phase0-gate.md`  
**Evidence:** 33/33 unit tests (ETM §3 GSM guards + Invariant pass)

## What is next?

1. **MB2 Phase 1** — D1 `observe.py` + `test_observe.py` per rebased spec §3
2. Branch `mb2-adaptive-runtime` from Phase 0 baseline (optional per L2 plan)

Product M5 orthogonal (Critic §12 pending).
