# Engineering WorkOrder Proposal — PX3-EWO-009

> **Status:** **REGISTERED — NOT AUTHORIZED** (await PX3-EWO-008 PASS)

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  classification_mode: retrospective
  classification_pass: px3-20260706-v1
  classification_registry: .asep/registry/platform-classification.yaml
  classified_on: 2026-07-06
  category: B
  hypothesis_id: H-06
  success_metric: "Job FSM vocabulary observation §5; .asep/reports/PX3-EWO-009-job-fsm-observation.md PASS"
  exit_id: n/a
  program_mode: product
```

Program: `.asep/programs/thesisos-product-v2.yaml`  
Wave: `px3-parallel/wave_c_job_fsm`  
Spec: `docs/product/specs/px3-knowledge-experience-v2.md` §10  
SoR: `docs/superpowers/specs/mb2-engineering-runtime-spec.md` §5  
Backlog: `.asep/reports/PX3-WAVE-C-BACKLOG.md`

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX3-EWO-009 |
| **Sub-agent** | B |
| **Type** | **EWO** — Conformance |
| **EWO category** | **Alignment** |
| **Wave objective** | Execution & Job State Observation |
| **Milestone** | PX-3 Knowledge Experience (Conformance Program) |
| **Depends on** | PX3-EWO-008 |

---

## Conformance contract

| Field | Value |
|-------|-------|
| **Primary objective (SoR)** | Job FSM Observation (§5) — vocabulary alignment: projection aggregate states ↔ Job FSM subset |
| **Secondary objective (Product)** | Knowledge Graph §10 (lifecycle badges, bounded graph) |
| **SoR sections exercised** | §5 Job FSM |
| **Expected invariants** | INV-R-11 |
| **Expected MB2 gates** | — (Observable ≠ Qualified) |

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

## Ownership (exclusive)

```text
frontend/components/knowledge/graph/**
frontend/app/knowledge/graph/**
backend/app/api/knowledge.py              (graph endpoints if needed)
backend/app/services/knowledge/**         (graph data only)
.asep/reports/PX3-JOB-FSM-OBSERVATION-*.md
```

**Forbidden:** JobState transition enforcement, `TransitionError`, `JobClaimed` events, `builder_engine/`.

---

## Scope

### In scope

1. Status vocabulary alignment report — projection `waves.*.status` / `jobs.*.status` → §5.3 aggregate roll-up
2. Explicit distinction: PX-3 §4 lifecycle vs MB2 §5 Job FSM vocabulary
3. Knowledge Graph §10 — 15-node default, 100 hard limit, List fallback
4. Explain Page `[ Grafo ]` quick nav → `/knowledge/graph`
5. Read-only job status from projection — never written by product (INV-R-11)

### Out of scope

- Illegal transition proof (Runtime scope)
- Program Trace (EWO-008)
- Integration C (EWO-010)
- Forced §11 FAIL paths

---

## Acceptance criteria

- [ ] Vocabulary mapping table in EWO report
- [ ] Knowledge Graph §10 limits enforced
- [ ] Explain → Graph navigation works
- [ ] INV-R-11 evidenced (read-only consumer)
- [ ] `covers` evidenced in report
- [ ] `make ci` green; Wave A/B regression preserved

---

## References

- Backlog: `.asep/reports/PX3-WAVE-C-BACKLOG.md`
- Template: `.asep/templates/conformance-ewo-template.md`
