# PX-3 Wave B — Backlog Definition

> **Authority:** Architect  
> **Date:** 2026-07-05  
> **Status:** **APPROVED — DISPATCH AUTHORIZED**  
> **Review:** `.asep/reports/PX3-ARCHITECT-DECISION-20260705-WAVE-B-BACKLOG-REVIEW.md`  
> **Dispatch receipt:** `.asep/reports/PX3-AUTHORIZATION-WAVE-B-20260705.md`  
> **Program:** `.asep/programs/thesisos-product-v2.yaml`  
> **Parallel:** `.asep/programs/px3-parallel.yaml`

---

## Wave objective (SoR-first)

**Wave B — Projection Conformance**

| Tier | Target | PX-3 exercisability |
|------|--------|---------------------|
| **Primary** | §9 Projection Conformance | Yes |
| **Secondary** | §10 Supervisor Interaction Observation | Observable |
| **Optional** | §11 Failure semantics | Observable — natural paths only; never forced |

**Verifiable SoR delta vs Wave A:** §9 Projection → evidenced; §10 Supervisor → observation evidence attached.

Product vehicle (secondary): Explain Page regions A–B with loading/ready states — not the wave name.

---

## Wave B exit criteria (PASS)

Wave B is **PASS** only when **all** of:

1. **PX3-EWO-005**, **PX3-EWO-006**, **PX3-EWO-007** each report PASS  
2. **Conformance Integration B** (EWO-007) verdict PASS  
3. Conformance Log: **no N-class** entries attributable to Wave B  
4. `MB2-CONFORMANCE-COVERAGE.md`: **≥1 new** row at **Yes** or **Observable** vs post–Wave A baseline  

```text
Coverage_after := union(Wave B EWO.covers)
Requirement: |{rows newly Yes or Observable}| ≥ 1
```

---

## Wave B DAG

```text
PX3-EWO-005  Projection Conformance (§9)
      │
      ▼
PX3-EWO-006  Supervisor Interaction Observation (§10)
      │
      ▼
PX3-EWO-007  Conformance Integration B
```

| EWO | Title | Primary (SoR) | Secondary (Product) |
|-----|-------|---------------|---------------------|
| **PX3-EWO-005** | Projection Conformance | §9 — read-only projection artifact (INV-R-11) | Explain Page shell regions A–B; loading/ready states |
| **PX3-EWO-006** | Supervisor Interaction Observation | §10 — observe AUTHORIZE/WAIT contract; **do not exercise Runtime Supervisor** | Async concept load; WAIT evidence in EWO report |
| **PX3-EWO-007** | Conformance Integration B | §9 projection union + SoR evidence merge | Cross-module wiring; `make ci`; coverage matrix update |

**First executable EWO:** `PX3-EWO-005`

---

## EWO conformance contracts (`covers:` max 3 elements)

### PX3-EWO-005 — Projection Conformance

```yaml
covers:
  sor_sections:
    - "§9 Projection"
  invariants:
    - INV-R-11
  mb2_gates:
    - MB2-Q5
  px3_exercisability: Yes
  class: A
```

### PX3-EWO-006 — Supervisor Interaction Observation

```yaml
covers:
  sor_sections:
    - "§10 Supervisor interaction"
  invariants:
    - INV-R-16
  mb2_gates: []
  px3_exercisability: Observable
  class: B
```

**Note:** PX-3 **observes** Supervisor interaction patterns (AUTHORIZE, WAIT, escalation
documentation). It does **not** implement or exercise the Runtime Supervisor.

§11: report only if failure occurs naturally — not an acceptance criterion.

### PX3-EWO-007 — Conformance Integration B

```yaml
covers:
  sor_sections:
    - "§9 Projection"
  invariants:
    - INV-R-12
  mb2_gates: []
  px3_exercisability: Yes
  class: A
```

Deliverable: `.asep/reports/PX3-INTEGRATION-B.md` — conformance verdict + coverage delta.

---

## Explicit exclusions

| Exclusion | Reason |
|-----------|--------|
| Runtime Supervisor implementation | Observable only in PX-3 |
| Forced FAIL paths for §11 | Optional / natural only |
| Execution Graph primary EWO | Deferred |
| Plugin / Event Bus / Recovery | No (Runtime) / No (Qualification) |
| `builder_engine/` | PX-3 product-only |

---

## Authoritative sources

| Artifact | Role |
|----------|------|
| `docs/superpowers/specs/mb2-engineering-runtime-spec.md` | SoR §9, §10 (read-only) |
| `docs/product/specs/px3-knowledge-experience-v2.md` | Explain Page §9 (product vehicle) |
| `.asep/templates/conformance-ewo-template.md` | EWO contract |
| `.asep/reports/MB2-CONFORMANCE-COVERAGE.md` | Live matrix |

---

## Registration

| Artifact | Path |
|----------|------|
| PX3-EWO-005 proposal | `.asep/proposals/PX3-EWO-005-projection-conformance.md` |
| PX3-EWO-006 proposal | `.asep/proposals/PX3-EWO-006-supervisor-interaction-observation.md` |
| PX3-EWO-007 proposal | `.asep/proposals/PX3-EWO-007-conformance-integration-b.md` |
| Program entries | `thesisos-product-v2.yaml` workorder_backlog |
| Parallel waves | `px3-parallel.yaml` wave_b_* |

---

## WO-TRACE

```text
Backlog Review PASS → Program Graph registered → AUTHORIZE Wave B → PX3-EWO-005 (first)
```
