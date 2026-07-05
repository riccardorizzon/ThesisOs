# Engineering WorkOrder Proposal — PX3-EWO-008

> **Status:** **AUTHORIZED** — `.asep/reports/PX3-AUTHORIZATION-EWO-008-20260705.md`

Program: `.asep/programs/thesisos-product-v2.yaml`  
Wave: `px3-parallel/wave_c_execution_graph`  
SoR: `docs/superpowers/specs/mb2-engineering-runtime-spec.md` §4.2  
Backlog: `.asep/reports/PX3-WAVE-C-BACKLOG.md`

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX3-EWO-008 |
| **Sub-agent** | A |
| **Type** | **EWO** — Conformance |
| **EWO category** | **Alignment** |
| **Wave objective** | Execution & Job State Observation |
| **Milestone** | PX-3 Knowledge Experience (Conformance Program) |
| **Depends on** | PX3-EWO-007 (Wave B complete) |

---

## Conformance contract

| Field | Value |
|-------|-------|
| **Primary objective (SoR)** | Execution Graph Observation (§4.2) — observe Program→Execution structure; do not derive ReadySet |
| **Secondary objective (Product)** | Read-only Program Trace API + UI |
| **SoR sections exercised** | §4.2 Execution Graph |
| **Expected invariants** | INV-R-01 |
| **Expected MB2 gates** | — (Observable ≠ MB2-Q1) |

```yaml
covers:
  sor_sections:
    - "§4.2 Execution Graph"
  invariants:
    - INV-R-01
  mb2_gates: []
  px3_exercisability: Observable
  class: B
```

---

## Ownership (exclusive)

```text
backend/app/api/conformance.py              (program-graph endpoint extensions)
backend/app/services/conformance/**         (program graph read-only parser)
frontend/components/conformance/**          (Program Trace panel)
frontend/app/**/conformance/**              (dev/conformance route if needed)
.asep/reports/PX3-EXECUTION-GRAPH-OBSERVATION-*.md
```

**Forbidden:** `builder_engine/`, ReadySet computation, Dependency Engine, Event Bus.

---

## Scope

### In scope

1. Read-only API returning parsed `px3-parallel.yaml` waves, workorders, merge_order, depends_on
2. Program Trace UI — wave DAG display (conformance/dev surface, not primary nav)
3. INV-R-01 audit table in EWO report — every node maps 1:1 to Program Graph declaration
4. INV-R-12 boundary documented — consumer does not compute scheduling decisions
5. Tests asserting no ready-set fields exposed

### Out of scope

- Runtime derivation (ReadySet, CriticalPath)
- Knowledge Graph (EWO-009)
- Integration C (EWO-010)

---

## Acceptance criteria

- [ ] Program Graph entities visible read-only via API
- [ ] INV-R-01 audit table in EWO report
- [ ] INV-R-12 boundary documented; no ReadySet in API response
- [ ] Program Trace panel renders wave DAG
- [ ] `covers` evidenced in report; Conformance Log updated for any I/S/A/N
- [ ] `make ci` green; Wave A/B regression preserved

---

## References

- Backlog: `.asep/reports/PX3-WAVE-C-BACKLOG.md`
- Template: `.asep/templates/conformance-ewo-template.md`
- Coverage: `.asep/reports/MB2-CONFORMANCE-COVERAGE.md`
