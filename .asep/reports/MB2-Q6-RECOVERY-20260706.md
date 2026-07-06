# MB2-Q6 — Recovery Qualification

> **Gate:** MB2-Q6 — Recovery  
> **Verdict:** **PASS**  
> **Program:** px-exec — Execution Orchestration Platform  
> **Authorization:** `.asep/reports/PX-EXEC-AUTHORIZATION-MB2-Q6-20260706.md`  
> **Prerequisites:** MB2-Q1 PASS, MB2-Q2 PASS, MB2-Q3 PASS  
> **SoR revision:** 2026-07-05 (read-only)  
> **Timestamp:** 2026-07-06T05:55:00+02:00  

---

## Summary

MB2-Q6 qualification **PASS** on minimal recovery module and existing Job FSM / Rule Engine
artifacts. Normative tests MB2-Q-016…018 cover auditable job retry, checkpoint replay, and
PX-2 golden path rule sequence.

**Does not satisfy:** MB2 promotion (requires all MB2-Q1…Q6 + full §13.3 bundle audit),
px-exec-15 full EWO, Phase 4 AgentProvider.

---

## Gate criteria (SoR §13.2)

| Criterion | Result |
|-----------|--------|
| FAILED → READY emits audit | ✓ MB2-Q-016 |
| Checkpoint + replay restores queue | ✓ MB2-Q-017 |
| PX-2 golden path replay | ✓ MB2-Q-018 |

---

## Normative test evidence

| Test ID | Requirement | SoR / INV | Result | Module |
|---------|-------------|-----------|--------|--------|
| **MB2-Q-016** | FAILED → READY + RecoveryTaskCreated | §12, REQ-15 | **PASS** | `test_mb2_q6.py` |
| **MB2-Q-017** | Checkpoint + event replay restore queue | §12, REQ-15 | **PASS** | `test_mb2_q6.py` |
| **MB2-Q-018** | PX-2 golden path rule replay | §13.3, REQ-16 | **PASS** | `test_mb2_q6.py` |

```text
make unit-builder-engine → 153 passed (includes 3 MB2-Q6 normative tests)
```

Supporting evidence:

- `builder_engine/recovery.py` — retry_failed_job, checkpoint/restore, event replay
- `builder_engine/replan.py` — Replanned / RecoveryTaskCreated on validation fail
- `builder_engine/tests/test_mb2_q2.py` — MB2-Q-006 golden rules (Q-018 cross-ref)

---

## Traceability (§14.2 rows — MB2-Q6 gate)

| Req ID | Requirement | Gate | Test | Result |
|--------|-------------|------|------|--------|
| REQ-15 | Recovery auditable | MB2-Q6 | MB2-Q-016…017 | PASS |
| REQ-16 | PX-2 golden path replay | MB2-Q6 | MB2-Q-018 | PASS |

---

## Scope guard

| Artifact | Role |
|----------|------|
| `builder_engine/recovery.py` | **New** — minimal §12 recovery helpers |
| `builder_engine/tests/test_mb2_q6.py` | **New** — qualification only |
| Full px-exec-15-recovery-policies | **Not claimed** — Phase 4 scope |

---

## Phase 1 boundary (sor-compatibility)

| SoR intent | Phase 1 qualification scope |
|------------|-------------------------------|
| Wave replay / operator recovery | Advisory replan only (`replan.py`); no STATE auto-write |
| Checkpoint restore | In-memory checkpoint + event-log replay |
| MB2-Q-018 golden path | Rule-engine replay (same evidence class as MB2-Q-006) |

---

## Explicit exclusions

| Exclusion | Reason |
|-----------|--------|
| MB2-Q4 (Plugin Registry) | Not authorized |
| MB2 promotion | Requires Architect ratification of full gate bundle |
| AgentProvider / multi-program queue | Phase 4 (REQ-17) |
| Automated PX-2 wave execution replay | Promotion bundle — not this gate alone |

---

## Verdict

**MB2-Q6 PASS** — Recovery gate satisfied for Phase 1 Runtime Foundation.

Certificate: `.asep/certificates/MB2-Q6-20260706.yaml`
