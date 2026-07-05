# PX3-EWO-009 — Job FSM Observation

> **WorkOrder:** PX3-EWO-009  
> **Wave:** C — Job FSM Observation  
> **Status:** **PASS**  
> **Authorization:** `.asep/reports/PX3-AUTHORIZATION-EWO-009-20260705.md`  
> **Date:** 2026-07-05

---

## Conformance contract

```yaml
covers:
  sor_sections:
    - "§5 Job FSM"
  invariants:
    - INV-R-11
  mb2_gates: []
  px3_exercisability: Observable
  class: B
```

---

## Primary objective — Job FSM Observation (§5)

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Vocabulary mapping table | **PASS** | `.asep/reports/PX3-JOB-FSM-OBSERVATION-20260705.md` |
| Product §4 vs MB2 §5 distinction | **PASS** | Three-domain table + UI labels |
| Aggregate → Job FSM subset mapping | **PASS** | `backend/app/services/conformance/job_fsm.py` |
| Read-only consumer (INV-R-11) | **PASS** | GET-only `/conformance/job-fsm`; no mutation routes |
| No transition enforcement | **PASS** | No `TransitionError`, `JobClaimed`, or JobState engine |
| Observation artifact | **PASS** | `.asep/reports/PX3-JOB-FSM-OBSERVATION-20260705.md` |

---

## Secondary objective — Knowledge Graph §10

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Default 15-node limit | **PASS** | `DEFAULT_VISIBLE_NODES = 15` |
| Hard limit 100 + list fallback | **PASS** | `HARD_NODE_LIMIT`; list view toggle |
| Lifecycle badges on nodes | **PASS** | `KnowledgeGraphPanel` — §4 badges only |
| Explain `[ Grafo ]` nav | **PASS** | `ExplainHeaderBar` → `/knowledge/graph?focus=&depth=1` |
| Explorer Grafo link | **PASS** | `KnowledgeConceptCard` |
| Job FSM strip (separate domain) | **PASS** | `JobFsmObservationStrip` on graph page |

---

## Tests

| Suite | Result |
|-------|--------|
| `backend/tests/test_job_fsm_observation.py` | **6/6 PASS** |
| `backend/tests/test_knowledge_graph.py` | **6/6 PASS** |
| `frontend/components/knowledge/graph/KnowledgeGraphPanel.test.tsx` | **3/3 PASS** |
| `make ci` | **PASS** (373 backend + 243 frontend + 65 builder_engine) |

---

## Conformance Log

**No entries.** N-class: **0**.

---

## Coverage delta

| SoR row | Before | After |
|---------|--------|-------|
| §5 Job FSM | ❌ | **⏳ → evidenced (Observable)** |

Structured observation attached; not full Runtime proof (MB2-Q4 deferred).

---

## STOP

```text
PX3-EWO-009 PASS — STOP

Wave C: EWO-010 NOT authorized.
Await Architect review before AUTHORIZE PX3-EWO-010.
```

---

## WO-TRACE

```text
AUTHORIZE EWO-009 → observe §5 → PASS → STOP
```

---

```text
Milestone Status: PASS
Repository Status: main @ HEAD (+ EWO-009 product changes), working tree dirty
Remaining Scope: PX3-EWO-010 (withheld)
Known Risks: Coverage matrix not updated this EWO (no governance modification per operator constraint)
Recommended Next Action: Architect review → AUTHORIZE PX3-EWO-010 when ready
```
