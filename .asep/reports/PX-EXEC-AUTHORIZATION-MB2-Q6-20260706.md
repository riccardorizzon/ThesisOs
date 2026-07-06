# Architect Authorization — MB2-Q6 Qualification

Program: px-exec  
Milestone: MB2 — Engineering Runtime  
Gate: **MB2-Q6** — Recovery  
Role: qualification (platform track)  
Status: **AUTHORIZED**  
Operator command: `ASEP: AUTHORIZE MB2-Q6 qualification`  
Prerequisites: MB2-Q1 PASS, MB2-Q2 PASS, MB2-Q3 PASS  
Timestamp: 2026-07-06T05:50:00+02:00  

---

## Intent resolution

```text
intent: authorize
program: px-exec
gate: MB2-Q6
role: qualification
scope: MB2-Q-016…018 — Recovery semantics (§12)
```

---

## Pre-flight summary

```text
Pre-flight: PASS
  ✓ MB2-Q1, MB2-Q2, MB2-Q3 PASS
  ✓ Job FSM recovery path present (FAILED → DEBUGGING → READY)
  ✓ Event catalog includes RecoveryTaskCreated, Replanned
  ✓ SoR frozen @ 2026-07-05
  ✓ make unit-builder-engine green (147 tests @ pre-qualification)
  ✓ Minimal recovery module authorized for qualification evidence
  ✓ MB2-Q4, MB2 promotion remain NOT AUTHORIZED
```

---

## Authorized qualification act

| Field | Value |
|-------|-------|
| **Gate** | MB2-Q6 — Recovery |
| **SoR §** | §12 Recovery semantics, §13.3 golden path |
| **Normative tests** | MB2-Q-016, MB2-Q-017, MB2-Q-018 |
| **Primary artifact** | `builder_engine/recovery.py` |
| **Qualification module** | `builder_engine/tests/test_mb2_q6.py` |
| **Supporting evidence** | `builder_engine/replan.py`, `builder_engine/job_queue.py` |

**Does not authorize:** MB2 promotion, Phase 4 AgentProvider, full px-exec-15 EWO

---

## WO-TRACE

```text
MB2-Q3 PASS → AUTHORIZE MB2-Q6 → qualify → MB2-Q6 report PASS | STOP
```
