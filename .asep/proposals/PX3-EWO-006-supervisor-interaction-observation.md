# Engineering WorkOrder Proposal — PX3-EWO-006

> **Status:** ✅ **IMPLEMENTED** — `.asep/reports/PX3-EWO-006-supervisor-interaction-observation.md` PASS

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  classification_mode: retrospective
  classification_pass: px3-20260706-v1
  classification_registry: .asep/registry/platform-classification.yaml
  classified_on: 2026-07-06
  category: B
  hypothesis_id: H-06
  success_metric: "Supervisor WAIT observable in Explain shell §10; report PASS"
  exit_id: X-08
  program_mode: product
```

Program: `.asep/programs/thesisos-product-v2.yaml`  
Wave: `px3-parallel/wave_b_supervisor`  
SoR: `docs/superpowers/specs/mb2-engineering-runtime-spec.md` §10

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX3-EWO-006 |
| **Sub-agent** | B |
| **Type** | **EWO** — Conformance |
| **EWO category** | **Alignment** |
| **Wave objective** | Projection Conformance (Wave B) |
| **Capability** | `px3-ewo-006-supervisor-interaction-observation` |
| **Milestone** | PX-3 Knowledge Experience (Conformance Program) |
| **Depends on** | PX3-EWO-005 |

---

## Conformance contract

| Field | Value |
|-------|-------|
| **Primary objective (SoR)** | **Supervisor Interaction Observation** (§10) — observe contract; do not exercise Runtime Supervisor |
| **Secondary objective (Product)** | Async concept detail load; WAIT-like UX where natural |
| **Product objective** | Explain Page async regions; escalation/WAIT documented in report |
| **SoR sections exercised** | §10 Supervisor interaction |
| **Expected invariants** | INV-R-16 |
| **Expected MB2 gates** | — |

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

**Critical:** PX-3 **observes** Supervisor interaction semantics (AUTHORIZE, WAIT, halt
until cleared). It does **not** implement or exercise the Engineering Runtime Supervisor.

---

## Objective

Collect **observation evidence** that product flows align with §10 contract expectations
without proving internal Supervisor behavior. Document AUTHORIZE/WAIT patterns in the
EWO report as conformance artifacts.

---

## Ownership (exclusive)

```text
frontend/components/knowledge/explain/**     (async load, WAIT UX — extends 005)
frontend/lib/knowledgeClient.ts              (async fetch patterns)
backend/app/api/knowledge.py                 (slow-path / error responses if needed)
.asep/reports/PX3-SUPERVISOR-OBSERVATION-*.md
```

**Forbidden:** `builder_engine/`, Runtime Supervisor, forced Integration FAIL for §11.

---

## Scope

### In scope

1. **Observation report** — maps product AUTHORIZE/WAIT moments to §10 + INV-R-16
2. **Async load** — Explain Page progressive region load with explicit WAIT/ready states
3. **Natural error paths** — log §11 only if encountered; not forced
4. **No Runtime Supervisor** — governance docs + product UX only

### Out of scope

- Engineering Supervisor automation changes
- Artificial failure injection
- Recovery semantics (§12)

---

## Acceptance criteria

- [ ] Supervisor Interaction Observation report attached (§10 mapping)
- [ ] INV-R-16 observation evidence (WAIT halts progression where applicable)
- [ ] Async Explain Page load demonstrable
- [ ] No forced §11 FAIL paths
- [ ] `covers` evidenced; Conformance Log for I/S/A/N
- [ ] `make ci` green

---

## References

- Backlog: `.asep/reports/PX3-WAVE-B-BACKLOG.md`
- EWO-005: `.asep/proposals/PX3-EWO-005-projection-conformance.md`
