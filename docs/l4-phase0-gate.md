# L4 Phase 0 Gate — GSM + Invariant Pass

_As of 2026-06-25. Branch `main`. Authority: `plans/l2-global-state-machine-plan.md` Ph1–2; MB2 spec §13 Architect Approved (spec only)._

This gate closes **L4 Phase 0** — prerequisite infrastructure only. It does **not** promote MB2 functional deliverables (D1–D11).

---

## Promotion decision

```yaml
promotion_decision: approved
phase: L4 Phase 0
status: closed
authorized_next: MB2 Phase 1 (D1 — Observe) — after this gate record is committed
```

---

## Gate checklist

| Criterion | Required | Result | Evidence |
|-----------|----------|--------|----------|
| **Scope** | L4 Phase 0 prereqs only (L2 plan Ph1–2) | ✅ green | Files listed §Delivered; no `observe.py`, `policy.py`, `events.py`, `cycle.py` |
| **Constitution** | No L0–L3 or ADR amendments | ✅ green | Diff excludes `docs/platform/{engineering-meta-model,invariant-model,behavioral-semantics,global-state-machine,runtime-model}*` |
| **Behavioral Semantics** | Unchanged | ✅ green | No new BS behaviors; implementation maps existing L2 T-* + L1 INV-* |
| **L2** | No new transitions | ✅ green | `gsm_task.py` implements frozen L2 §5.5 T-01–T-12 only |
| **L3** | No Runtime Cycle semantic change | ✅ green | `WorkflowRuntime` schedule/sync paths unchanged in intent; GSM delegation only |
| **Tests** | Unit suite green | ✅ green | 33/33 — §Evidence |
| **Evidence** | ETM-linked artifacts | ✅ green | ETM §2 rows (GSM guards, Invariant pass); this file |
| **Rollback** | Pre-Phase-0 baseline identified | ✅ green | `f117d3d` — `docs(knowledge): reflect MB2 rebase complete, sign-off §13 pending` |

---

## Gate YAML

```yaml
scope: l4_phase0_prerequisites_only
constitution_unchanged: true
behavioral_semantics_unchanged: true
l2_no_new_transitions: true
l3_runtime_cycle_unchanged: true
gsm_executable: green          # gsm_task.py + gsm.py
inv_a_guards: green            # INV-A1–A5 Class A
inv_b_pre_commit: green        # invariants.py + state_io hook
runtime_gsm_aligned: green     # schedule_packet / sync_validate_outcome
validate_unknown_dep_fix: green
unit_builder_engine: green     # 33 passed
sidecar_boundary: green        # no import backend.app in builder_engine/
mb2_deliverables: not_in_scope # D1–D11 deferred
promotion_decision: approved
rollback_baseline: f117d3d
phase0_baseline: see git tag l4-phase0-complete (this commit)
```

---

## Delivered (Phase 0 scope)

| Component | Path | L2 trace |
|-----------|------|----------|
| Task FSM (T-01–T-12) | `builder_engine/gsm_task.py` | L2 §5.5, §4.3 |
| GSM wrapper | `builder_engine/gsm.py` | L2 §5.5 |
| Class A guards | `gsm_task._assert_class_a` | L2 §8 INV-A* |
| Class B invariant pass | `builder_engine/invariants.py` | L1 §4, L2 §8 INV-B* |
| Pre-commit hook | `builder_engine/state_io.py` | INV-B8 |
| State machine delegate | `builder_engine/state_machine.py` | ADR-0025 shim |
| Runtime alignment | `builder_engine/runtime.py` | Schedule/Validate behaviors |
| validate fix | `builder_engine/validate.py` | unknown `depends_on` fail-closed |
| Tests | `test_gsm_task.py`, `test_invariants.py` | ETM §3 |

**Explicitly out of scope:** `observe.py`, `policy.py`, `events.py`, `cycle.py`, `EngineeringRuntime` rename (L2 plan Ph7 / MB2 D10).

---

## Evidence

### Unit tests (2026-06-25)

```bash
cd builder_engine && .venv/bin/pytest -q
```

```
.................................                                        [100%]
33 passed in 0.05s
```

Alternative (Makefile target):

```bash
make unit-builder-engine
```

### ETM traceability

| ETM §3 row | Module | Test | Evidence |
|------------|--------|------|----------|
| GSM guards | `gsm_task.py` | `test_gsm_task.py` | TransitionError on illegal; T-11/T-12 |
| Invariant pass | `invariants.py` | `test_invariants.py` | InvariantViolation halts commit |

See `docs/platform/engineering-traceability-matrix.md` §3–§5.

### Sidecar boundary

```bash
rg "import backend\.app|from backend\.app" builder_engine/
# (no matches expected)
```

---

## Rollback procedure

To revert Phase 0 and restore pre-prerequisite baseline:

```bash
git revert <phase0-commit>   # preferred: single revert of Phase 0 merge
# or
git checkout f117d3d -- builder_engine/
```

Pre-Phase-0 baseline: **`f117d3d`**.

---

## Authorization chain (closed)

```text
Constitution (frozen)
        ↓
MB2 Specification (Architect Approved 2026-06-25)
        ↓
L4 Phase 0 Implementation
        ↓
Unit Tests (33/33)
        ↓
Evidence (this gate + ETM)
        ↓
Commit + tag l4-phase0-complete
        ↓
Promotion Decision: Phase 0 → Approved
        ↓
MB2 Phase 1 (D1 — Observe) authorized
```

---

## References

- `plans/l2-global-state-machine-plan.md` Ph1–2
- `docs/superpowers/specs/2026-06-25-thesisos-mb2-adaptive-runtime-design.md` §13
- `docs/platform/engineering-traceability-matrix.md`
- ADR-0025, ADR-0028, ADR-0029, ADR-0023
