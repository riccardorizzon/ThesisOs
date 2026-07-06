# MB2-Q1 — Runtime Graph Qualification

> **Gate:** MB2-Q1 — Runtime Graph  
> **Verdict:** **PASS**  
> **Program:** px-exec — Execution Orchestration Platform  
> **Authorization:** `.asep/reports/PX-EXEC-AUTHORIZATION-MB2-Q1-20260706.md`  
> **SoR revision:** 2026-07-05 (read-only)  
> **Timestamp:** 2026-07-06T04:00:00+02:00  
> **Repository:** `main` @ `f5b1926` (+ qualification artifacts)

---

## Summary

MB2-Q1 qualification **PASS** for the Reference Implementation Dependency Engine
and supporting Job FSM (§5 partial via EWO-004). Normative tests MB2-Q-001…003 executed
and green. Wave A artifacts satisfy Phase 1 exit gate `implementation_gate: MB2-Q1-pass`
for the Runtime Graph scope defined in SoR §13.2.

**Does not satisfy:** MB2-Q2…Q6, MB2 promotion, or full Phase 1 product qualification.

---

## Gate criteria (SoR §13.2)

| Criterion | Result |
|-----------|--------|
| Program Graph → Execution Graph derivation | ✓ MB2-Q-001 |
| Illegal node / graph rejected | ✓ MB2-Q-001 supplement |
| No orphan executable nodes | ✓ MB2-Q-002 |
| merge_order respected (tie-breaker only) | ✓ MB2-Q-003 |
| §5 Job FSM (REQ-14 partial) | ✓ MB2-Q-001 supplement |

---

## Normative test evidence

| Test ID | Requirement | SoR / INV | Result | Module |
|---------|-------------|-----------|--------|--------|
| **MB2-Q-001** | Execution Graph derived only from Program Graph | §4.2, INV-R-02 | **PASS** | `test_mb2_q1.py` |
| **MB2-Q-001** | Illegal circular graph rejected | §4.1 | **PASS** | `test_mb2_q1.py` |
| **MB2-Q-001** | Job FSM legal transitions (REQ-14) | §5, ADR-0025 | **PASS** | `test_mb2_q1.py` |
| **MB2-Q-002** | No orphan executable nodes | INV-R-01 | **PASS** | `test_mb2_q1.py` |
| **MB2-Q-003** | merge_order respected | INV-R-03 | **PASS** | `test_mb2_q1.py` |
| **MB2-Q-003** | px-exec wave merge_order excerpt | §4.2 | **PASS** | `test_mb2_q1.py` |

```text
make unit-builder-engine → 138 passed (includes 6 MB2-Q1 tests)
```

Supporting EWO evidence (not duplicated as normative gate tests):

- `test_dependency_engine.py` — EWO-003 acceptance
- `test_job_queue.py` — EWO-004 FSM + events

---

## Traceability (§14.2 rows — MB2-Q1 gate)

| Req ID | Requirement | Gate | Test | Result |
|--------|-------------|------|------|--------|
| REQ-02 | Execution Graph is derived | MB2-Q1 | MB2-Q-001 | PASS |
| REQ-03 | Every node traces to Program Graph | MB2-Q1 | MB2-Q-002 | PASS |
| REQ-04 | merge_order enforced | MB2-Q1 | MB2-Q-003 | PASS |
| REQ-14 | Job FSM conforms ADR-0025 | MB2-Q1 | MB2-Q-001 (supplement) | PASS |

---

## Scope guard

| Path | Role |
|------|------|
| `builder_engine/dependency.py` | Primary — graph derivation |
| `builder_engine/program_graph.py` | Primary — Program Graph loader |
| `builder_engine/job_queue.py` | §5 supplement — FSM |
| `builder_engine/tests/test_mb2_q1.py` | Qualification tests |
| `backend/app/**`, `frontend/**` | Not touched |
| SoR | Not modified |

---

## Wave A prerequisites

| Prerequisite | Status |
|--------------|--------|
| PX-EXEC-EWO-001…006 IMPLEMENTED | PASS |
| PX-EXEC-INTEGRATION-WAVE-A | PASS |
| MB2 SoR frozen | PASS |

---

## Explicit exclusions

| Exclusion | Reason |
|-----------|--------|
| MB2-Q2 Rule Engine | Separate qualification act |
| MB2-Q3 Scheduler | Separate qualification act |
| MB2-Q4 Plugin Registry | Phase 2 |
| MB2-Q5 Projection | Separate qualification act |
| MB2-Q6 Recovery | Phase 4 |
| PX-2 golden path replay | MB2-Q6 / promotion bundle |

---

## Phase 1 exit gate

```text
implementation_gate: MB2-Q1-pass → SATISFIED (this report)
```

Remaining Phase 1 capabilities may proceed; full MB2 promotion requires MB2-Q1…Q6.

---

## WO-TRACE

```text
Wave A PASS → AUTHORIZE MB2-Q1 → test_mb2_q1.py → MB2-Q1 PASS
  → Next: AUTHORIZE MB2-Q2 (optional) | Phase 2 planning
```
