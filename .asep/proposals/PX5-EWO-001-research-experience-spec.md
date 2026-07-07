# Engineering WorkOrder Proposal — PX5-EWO-001

> **Status:** **AUTHORIZED** — `.asep/reports/PX5-AUTHORIZATION-20260706.md`

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  category: A
  hypothesis_id: n/a
  success_metric: "PX-5 product spec ratified with INV-KM-5 boundary preserved"
  exit_id: n/a
  program_mode: product
```

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX5-EWO-001 |
| **Title** | Research Experience Spec + UX foundation |
| **Milestone** | PX-5 |
| **Layer** | Business |

## Objective

Ratify the **PX-5 Research Experience** product specification and UI spec draft,
defining the spatial research canvas scope and explicit boundaries vs PX-3 guided
research and PX-4 Knowledge Graph.

## Deliverables

- `docs/product/specs/px5-research-experience-v1.md` — normative product spec
- `design-system/thesisos/px5-research-experience-ui-spec.md` — UI spec draft
- `.asep/reports/PX5-EWO-001-research-experience-spec.md` — PASS report

## Acceptance

- [x] Product spec covers canvas scope, discovery, node semantics, and Writing handoff
- [x] UI spec defines layout, interaction model, and limits (distinct from PX-3 graph §10)
- [x] Boundary table: PX-3 guided `/research` vs PX-4 `/knowledge/graph` vs PX-5 canvas
- [x] INV-KM-5 preserved — builds on PX-4 concept model, no bypass
- [x] No implementation code in this EWO (spec-only)

## Dependencies

- PX-4 promoted (`px4-complete`)
- PX-3 conformance complete

## Forbidden

- Modifying SoR, Runtime Constitution, or `builder_engine/` MB2 surfaces
- Expanding PX-3 Knowledge Graph limits into canvas scope
- Shipping canvas UI before spec ratification
