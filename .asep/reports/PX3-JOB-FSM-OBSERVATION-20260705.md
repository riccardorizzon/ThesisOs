# PX3 Job FSM Observation — Structured Artifact

> **WorkOrder:** PX3-EWO-009  
> **Wave:** C — Job FSM Observation  
> **Date:** 2026-07-05  
> **Authorization:** `.asep/reports/PX3-AUTHORIZATION-EWO-009-20260705.md`

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

## Vocabulary mapping table

Three domains — **must not be conflated** in UI or reports.

| Domain | Vocabulary | Values | Product surface |
|--------|------------|--------|-----------------|
| **Product lifecycle** | PX-3 §4 | `candidate`, `validated`, `linked`, `referenced`, `deprecated` | Knowledge Graph node badges (`KnowledgeLifecycleBadge`) |
| **MB2 aggregate** | SoR §5.3 projection roll-up | `waiting`, `ready`, `running`, `pass`, `fail`, `locked` | `GET /conformance/projection` → `waves.*.status`, `jobs.*.status` |
| **Job FSM subset** | SoR §5.1 (display only) | `CREATED`, `READY`, `CLAIMED`, `RUNNING`, … | `GET /conformance/job-fsm` → `projection_jobs[].job_fsm_subset` |

### Aggregate → Job FSM subset (observation mapping)

| §5.3 aggregate | §5.1 subset (display) | Label |
|----------------|----------------------|-------|
| `waiting` | `CREATED` | Pre-queue / blocked |
| `ready` | `READY` | Eligible for claim |
| `running` | `RUNNING` | Active execution |
| `pass` | `DONE` | Terminal success (EWO complete) |
| `fail` | `FAILED` | Terminal failure |
| `locked` | `LOCKED` | Claim held — scheduler scope |

### Program status → aggregate (projection builder)

| Program Graph `status` | §5.3 aggregate |
|------------------------|----------------|
| `implemented`, `qualified`, `complete` | `pass` |
| `approved` | `ready` |
| `in_progress` | `running` |
| `blocked` | `waiting` |
| `failed` | `fail` |
| *(default / missing)* | `waiting` |

**Not in scope:** illegal transition proof, `TransitionError`, `JobClaimed` events — Runtime scope (ADR-0025).

---

## INV-R-11 evidence

| Check | Result | Evidence |
|-------|--------|----------|
| Projection read-only | **PASS** | GET-only `/conformance/projection`, `/conformance/job-fsm` |
| Product never writes job state | **PASS** | No POST/PUT/PATCH on conformance routes; graph API read-only |
| Job status from projection only | **PASS** | `JobFsmObservationStrip` consumes `getJobFsmObservation()` |
| Non-authoritative labeling | **PASS** | UI copy: "read-only consumer (INV-R-11)" |

---

## Knowledge Graph §10 evidence

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Default 15 nodes | **PASS** | `DEFAULT_VISIBLE_NODES = 15` in schema + API |
| Hard limit 100 | **PASS** | `HARD_NODE_LIMIT = 100`; `view=list` fallback |
| Soft limit 50 banner | **PASS** | `show_performance_banner` when > 50 |
| Lifecycle badges on nodes | **PASS** | `KnowledgeGraphPanel` — §4 badges only |
| List view fallback | **PASS** | Toggle + forced list at hard limit |
| Explain → Graph nav | **PASS** | `ExplainHeaderBar` `[ Grafo ]` → `/knowledge/graph?focus=&depth=1` |
| Explorer → Graph nav | **PASS** | `KnowledgeConceptCard` Grafo link |

---

## API surfaces

| Endpoint | Purpose |
|----------|---------|
| `GET /projects/{id}/conformance/job-fsm` | Vocabulary domains + projection job observation |
| `GET /projects/{id}/knowledge/graph` | Bounded concept graph (focus, depth, max_nodes) |

---

## Sample projection jobs (2026-07-05 rebuild)

Derived from `build_px3_projection()` — see live API for current values.

| EWO | Aggregate | Job FSM subset | Wave |
|-----|-----------|----------------|------|
| PX3-EWO-001 … EWO-007 | `pass` | `DONE` | wave_a_* / wave_b_* |
| PX3-EWO-008 | `pass` | `DONE` | wave_c_execution_graph |
| PX3-EWO-009 | `waiting` | `CREATED` | wave_c_job_fsm |
| PX3-EWO-010 | `waiting` | `CREATED` | wave_c_conformance_integration |

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

## Files touched (product)

```text
backend/app/schemas/knowledge_graph.py
backend/app/schemas/job_fsm_observation.py
backend/app/services/conformance/job_fsm.py
backend/app/services/knowledge/graph.py
backend/app/api/conformance.py
backend/app/api/knowledge.py
backend/tests/test_job_fsm_observation.py
backend/tests/test_knowledge_graph.py
frontend/lib/jobFsmVocabulary.ts
frontend/lib/knowledgeTypes.ts
frontend/lib/knowledgeClient.ts
frontend/components/knowledge/graph/**
frontend/app/knowledge/graph/page.tsx
frontend/components/knowledge/explain/ExplainHeaderBar.tsx
frontend/components/knowledge/explorer/KnowledgeConceptCard.tsx
.asep/reports/PX3-JOB-FSM-OBSERVATION-20260705.md
```

---

## STOP

```text
PX3-EWO-009 PASS — STOP

Wave C: EWO-010 NOT authorized.
Await Architect review before AUTHORIZE PX3-EWO-010.
```

---

```text
Milestone Status: PASS
Repository Status: main @ HEAD (+ EWO-009 product changes)
Remaining Scope: PX3-EWO-010 (withheld)
Known Risks: Coverage matrix not updated this EWO (no governance modification per operator constraint)
Recommended Next Action: Architect review → AUTHORIZE PX3-EWO-010 when ready
```
