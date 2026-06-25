# L2 Global State Machine — Implementation & Migration Plan

> **For agentic workers:** This plan implements **L4 (MB2)** by concretizing the frozen L2 GSM. **No code until this plan and the rebased MB2 spec are approved.** REQUIRED SUB-SKILL: superpowers:executing-plans or subagent-driven-development.

**Goal:** Make the Global State Machine executable in `builder_engine/` — transitions, guards, events, invariant enforcement — without violating L0–L3 or sidecar boundaries (ADR-0023).

**Authority chain:**

```text
L0 engineering-meta-model.md
L1 invariant-model.md
L2 global-state-machine.md          ← this plan implements
L3 runtime-model.md
L4 MB2 implementation spec (rebased)
```

**Branch:** `mb2-adaptive-runtime` (from `main` after L2 freeze commit).

**Tech stack:** Python 3.11+, dataclasses, Typer CLI, pytest. No new dependencies.

**Conventions:** TDD for FSM and invariant guards; additive CLI; M0–M4 + `builder_engine` tests green after every phase.

---

## Prerequisites (before Phase 1)

| # | Deliverable | Status |
|---|-------------|--------|
| P-1 | L2 GSM frozen (`docs/platform/global-state-machine.md`) | Required |
| P-2 | Rebase `docs/superpowers/specs/…-mb2-adaptive-runtime-design.md` — every deliverable traces to L2 transition ID | Required |
| P-3 | Architect sign-off on rebased MB2 spec | Required |
| P-4 | Critic pass on L2 GSM §12 gap list | Recommended |

---

## Incremental migration strategy

Era I continues to work throughout. Migration is **additive**, not big-bang.

```text
Phase 1   Formal FSM module (all T-* + guards)     — no YAML schema change
Phase 2   Class B invariant pass before commit      — stricter, may surface latent bugs
Phase 3   Optional execution_state in STATE.yaml    — backward compatible
Phase 4   Cycle orchestrator + Snapshot FSM         — new CLI `cycle`
Phase 5   Build event bus                           — append-only JSONL
Phase 6   Recovery CLI (debug/retry)                — replaces manual YAML edits
Phase 7   WorkflowRuntime → EngineeringRuntime      — rename + rebase MB2 spec close-out
```

**Rollback:** each phase is independently revertible. Phase 3 is feature-flagged (`execution_state` optional field).

---

## Phase 1 — Executable Task FSM (T-* complete)

### Objective
Replace ad-hoc transitions in `runtime.py` with GSM-authoritative `GlobalStateMachine` module wrapping ADR-0025 + L2 T-11, T-12.

### Files
| Action | Path |
|--------|------|
| Create | `builder_engine/gsm.py` — `GlobalStateMachine`, transition registry from L2 §5.5 |
| Create | `builder_engine/gsm_task.py` — Task entity transitions, INV-A guards |
| Modify | `builder_engine/state_machine.py` — delegate to gsm or deprecate with shim |
| Modify | `builder_engine/runtime.py` — call GSM for schedule/sync |
| Create | `builder_engine/tests/test_gsm_task.py` — every T-* row + illegal transition |

### Promotion criteria
- [ ] All T-01–T-12 transitions executable with `TransitionError` on illegal
- [ ] INV-A1–A5 enforced as Class A guards
- [ ] Existing `test_state_machine.py` green (or migrated)
- [ ] `make unit-builder-engine` green

### L2 traceability
| Deliverable | L2 section |
|-------------|------------|
| Task transitions | §5.5, §4.3 |
| INV-A guards | §8 |

---

## Phase 2 — Invariant layer (Class B pass)

### Objective
Centralized fail-closed pass before every StateWriter commit (L1 §4, L2 §8).

### Files
| Action | Path |
|--------|------|
| Create | `builder_engine/invariants.py` — `InvariantViolation`, `check_all(candidate_graph)` |
| Modify | `builder_engine/validate.py` — split errors (invariants) from warnings (policy hints) |
| Modify | `builder_engine/state_io.py` — hook invariant pass pre-commit |
| Create | `builder_engine/tests/test_invariants.py` — INV-B1–B9 where testable |

### Promotion criteria
- [ ] INV-B4, B5, B6, B8 enforced on commit (extend existing validate.py coverage)
- [ ] INV-B3 at schedule/claim time
- [ ] InvariantViolation halts with clear message (never warning)
- [ ] `make unit-builder-engine` green

### L2 traceability
| Deliverable | L2 section |
|-------------|------------|
| Class B pass | §8, L1 §4 |
| Gap closure | §12 INV-A1–A4, B3 |

---

## Phase 3 — YAML projection upgrade (optional field)

### Objective
Close GSM §12 YAML projection gap without breaking Era I STATE files.

### Files
| Action | Path |
|--------|------|
| Modify | `builder_engine/state_io.py` — read/write optional `execution_state` per packet |
| Modify | `builder_engine/graph.py` — expose `execution_state` if present |
| Modify | `.cursor/skills/orchestrate-builders/references/packet-template.yaml` — document field |

### Rules
- If `execution_state` absent → infer from `status` (Era I compat)
- If present → authoritative for Task FSM; `status` is derived projection

### Promotion criteria
- [ ] Existing STATE.yaml without field still loads
- [ ] New schedules write both fields
- [ ] CLAIMED, VALIDATING, MERGED distinguishable in new state files

### L2 traceability
§11 Era I projection map

---

## Phase 4 — Snapshot FSM + Cycle orchestrator (S-*, C-*)

### Objective
Implement L3 cycle as explicit state machine; unified Observe read model.

### Files
| Action | Path |
|--------|------|
| Create | `builder_engine/observe.py` — S-01, S-02, `ObservedSnapshot` |
| Create | `builder_engine/cycle.py` — C-01–C-15 orchestrator |
| Modify | `builder_engine/cli.py` — `builder-engine cycle` command |
| Create | `builder_engine/tests/test_observe.py`, `test_cycle.py` |

### Promotion criteria
- [ ] `cycle --dry-run` walks C-01→C-02→C-05→C-06 without side effects
- [ ] Snapshot immutable after seal
- [ ] Stale snapshot aborts before schedule (STALE_SNAP)

### L2 traceability
§5.8, §5.10, §4.8

### MB2 spec rebase targets
Observe, extended Plan, `EngineeringRuntimeCycle` (from superseded MB2 spec)

---

## Phase 5 — Build event bus (L4)

### Objective
Every GSM transition emits typed event to append-only bus (L2 §7).

### Files
| Action | Path |
|--------|------|
| Create | `builder_engine/events.py` — event types, `EventBus`, JSONL writer |
| Modify | `builder_engine/gsm.py` — emit on successful transition |
| Modify | `builder_engine/cycle.py` — C-12 publish phase |
| Create | `builder_engine/tests/test_events.py` |

### Storage
Default: `.builder-engine/events.jsonl` (append-only, ADR-0028 MB2 note).

### Promotion criteria
- [ ] Every T-* success emits ≥1 event
- [ ] Events queryable by type and transition ID
- [ ] No event without transition (L2 §7 rule)

### L2 traceability
§7 Event matrix

---

## Phase 6 — Recovery CLI (T-08, T-09)

### Objective
Replace manual YAML recovery with explicit GSM transitions.

### Files
| Action | Path |
|--------|------|
| Modify | `builder_engine/cli.py` — `debug`, `retry` commands |
| Modify | `builder_engine/gsm_task.py` — T-08, T-09 |

### Promotion criteria
- [ ] `builder-engine debug P-XXX` executes T-08 on blocked packet
- [ ] `builder-engine retry P-XXX` executes T-09 → T-02 path
- [ ] Recovery never skips FAILED (§9.2 forbidden pattern test)

### L2 traceability
§9 Recovery model

---

## Phase 7 — Rename + MB2 gate

### Objective
Align code with ADR-0026/0028 terminology; close MB2 implementation.

### Files
| Action | Path |
|--------|------|
| Rename | `WorkflowRuntime` → `EngineeringRuntime` in `runtime.py`, `cli.py`, tests |
| Create | `docs/mb2-phase-gate.md` |
| Modify | `docs/superpowers/specs/…-mb2-adaptive-runtime-design.md` — re-freeze |

### Promotion criteria
- [ ] No `WorkflowRuntime` references in `builder_engine/`
- [ ] MB2 spec §12 freeze record complete
- [ ] `make ci` green
- [ ] Gap analysis §12 items marked closed or explicitly deferred with ADR

---

## Policy Engine (L5) and Planner (L6) — out of scope for this plan

| Capability | Plan | GSM binding |
|------------|------|-------------|
| Policy Engine | MB2/MB3 follow-on | C-03, C-04; POL_* failures |
| Adaptive Planner | MB3 | C-14, T-09, E-02 |
| Promotion Engine automation | Control Plane tool | M-04 (manual OK in Era II) |
| Merge automation | Integrator worker | C-10, C-11 |

These **consume** L2 events; they do not redefine transitions.

---

## MB2 spec rebase checklist

When rebasing `docs/superpowers/specs/2026-06-25-thesisos-mb2-adaptive-runtime-design.md`:

| MB2 deliverable (original) | L2 transition IDs | L0 entity |
|----------------------------|-------------------|-----------|
| `ObservedSnapshot` | S-01, S-02 | Snapshot |
| Policy stub | C-03, C-04 | Policy (decision) |
| Extended Plan | T-01, C-05 | Task, Epic |
| Build event bus | §7 all | Event |
| Minimal Replan | T-09, C-14 | Task |
| `EngineeringRuntimeCycle` | C-01–C-15 | Cycle |
| `WorkflowRuntime` rename | Phase 7 | Engineering Runtime |

Remove any deliverable that does not trace to L2.

---

## Verification matrix (completion criteria)

| Criterion | Verified by |
|-----------|-------------|
| Every L0 entity lifecycle in code or Control Plane | Phase 1–7 + manual M/E/G |
| Every transition deterministic | `test_gsm_task.py` |
| Every transition one owner | Code module ownership matches §6 |
| Every transition has invariant | `test_invariants.py` + §8 table |
| Every event traceable | `test_events.py` |
| Every failure path modeled | `test_gsm_task.py` recovery tests |
| Recovery via GSM only | `test_recovery_no_skip.py` |
| MB2 derivable from L2 | MB2 spec rebase checklist above |

---

## Execution order summary

```text
1. Freeze L2 (this commit)
2. Rebase MB2 spec + Architect sign-off
3. Phase 1 Task FSM
4. Phase 2 Invariant layer
5. Phase 3 YAML projection (optional, can parallel Phase 5)
6. Phase 4 Cycle + Snapshot
7. Phase 5 Event bus
8. Phase 6 Recovery CLI
9. Phase 7 Rename + MB2 gate
```

**Estimated scope:** 7 implementation phases; Phases 1–2 are prerequisites for all others.

---

## References

- `docs/platform/global-state-machine.md` (L2 — authority)
- `docs/platform/engineering-meta-model.md` (L0)
- `docs/platform/invariant-model.md` (L1)
- `docs/platform/runtime-model.md` (L3)
- `decisions/ADR-0028-engineering-meta-model.md`
- `docs/superpowers/specs/2026-06-25-thesisos-mb2-adaptive-runtime-design.md` (to rebase)
