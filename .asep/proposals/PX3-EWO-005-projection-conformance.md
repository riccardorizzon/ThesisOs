# Engineering WorkOrder Proposal — PX3-EWO-005

> **Status:** ✅ **IMPLEMENTED** — `.asep/reports/PX3-EWO-005-projection-conformance.md` PASS

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  classification_mode: retrospective
  classification_pass: px3-20260706-v1
  classification_registry: .asep/registry/platform-classification.yaml
  classified_on: 2026-07-06
  category: B
  hypothesis_id: H-06
  success_metric: "Read-only projection API §9; report PASS — Observable, not MB2-Q qualified"
  exit_id: n/a
  program_mode: product
```

Program: `.asep/programs/thesisos-product-v2.yaml`  
Wave: `px3-parallel/wave_b_projection`  
Spec: `docs/product/specs/px3-knowledge-experience-v2.md` §9 (regions A–B, §9.16 states)  
SoR: `docs/superpowers/specs/mb2-engineering-runtime-spec.md` §9

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX3-EWO-005 |
| **Sub-agent** | A |
| **Type** | **EWO** — Conformance |
| **EWO category** | **Alignment** |
| **Wave objective** | Projection Conformance |
| **Capability** | `px3-ewo-005-projection-conformance` |
| **Milestone** | PX-3 Knowledge Experience (Conformance Program) |
| **Depends on** | PX3-EWO-004 (Wave A complete) |

---

## Conformance contract

| Field | Value |
|-------|-------|
| **Primary objective (SoR)** | Projection Conformance (§9) — read-only observability artifact; INV-R-11 |
| **Secondary objective (Product)** | Explain Page shell — regions A–B; loading/ready page states (§9.16) |
| **Product objective** | `/knowledge/[conceptSlug]` canonical concept view (partial — not full A–L) |
| **SoR sections exercised** | §9 Projection |
| **Expected invariants** | INV-R-11 |
| **Expected MB2 gates** | MB2-Q5 |

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

---

## Objective

Validate that product-side projection artifacts conform to SoR §9: **read-only**,
**rebuildable**, **non-authoritative**. Secondary: deliver Explain Page shell with
projection-consumer loading states — not full Explain Page (regions C–L deferred).

---

## Ownership (exclusive)

```text
frontend/app/knowledge/[conceptSlug]/**
frontend/components/knowledge/explain/**
backend/app/api/knowledge.py              (concept detail endpoint extensions only)
backend/app/schemas/knowledge.py          (projection-facing fields only)
.asep/reports/PX3-PROJECTION-*.yaml       (read-only projection artifact — if created)
```

**Forbidden:** Supervisor Runtime, `builder_engine/`, full graph (§10), forced failure paths.

---

## Scope

### In scope

1. **§9 projection artifact** — structured read-only document (YAML/JSON) derived from
   program/wave state; evidences INV-R-11 in EWO report
2. **Explain Page route** — `/knowledge/[conceptSlug]` with regions **A** (header) and **B** (definition)
3. **Page states** — loading skeletons, ready, not-found per §9.16
4. **Conformance evidence** — EWO report maps artifact fields to SoR §9 schema

### Out of scope

- Regions C–L (later waves)
- Runtime Projection Builder implementation
- Supervisor FSM (EWO-006)

---

## Acceptance criteria

- [ ] Read-only projection artifact attached; rebuild procedure documented
- [ ] INV-R-11 evidenced (projection does not own authoritative state)
- [ ] Explain Page A–B render with loading/ready/not-found states
- [ ] Explorer → Explain navigation works
- [ ] `covers` evidenced in report; Conformance Log updated for any I/S/A/N
- [ ] `make ci` green; PX-2 regression preserved

---

## References

- Backlog: `.asep/reports/PX3-WAVE-B-BACKLOG.md`
- Template: `.asep/templates/conformance-ewo-template.md`
- Coverage: `.asep/reports/MB2-CONFORMANCE-COVERAGE.md`
