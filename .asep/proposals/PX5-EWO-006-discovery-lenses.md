# Engineering WorkOrder Proposal — PX5-EWO-006

> **Status:** **AUTHORIZED** — `.asep/reports/PX5-AUTHORIZATION-WAVE-D-20260707.md`

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  category: A
  hypothesis_id: n/a
  success_metric: "Six discovery lenses reframe canvas subgraph per px5-research-experience-v1.md §6"
  exit_id: n/a
  program_mode: product
```

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX5-EWO-006 |
| **Title** | Discovery lenses + lens rail |
| **Milestone** | PX-5 |
| **Wave** | D |
| **Layer** | Business (Product Plane) |

## Objective

Implement discovery lenses (product §6) reframing the visible subgraph without
duplicate nodes (RR-2).

## Deliverables

- `frontend/lib/canvasLenses.ts` — lens definitions + filter predicates
- `frontend/components/research/canvas/ResearchLensRail.tsx` (UI spec §7)
- Header lens dropdown mirrors rail selection
- Filter popover: stato, relation type, core only, hide deprecated (UI spec §4.2)
- Lens catalog: L-all, L-gap, L-chapter, L-author, L-controversy, L-unread
- Filtered graph passed to viewport; lens switch preserves camera when possible
- Unit tests per lens predicate
- `.asep/reports/PX5-EWO-006-discovery-lenses.md`

## Acceptance

- [ ] All six lenses selectable; active lens indicated (accent border)
- [ ] L-controversy and L-gap produce deterministic subgraphs on stub + live graph
- [ ] L-chapter reads active chapter from Context packet when available; graceful empty when not
- [ ] L-author and L-unread: stub with catalog/dev fallback if backend lacks index — documented in report
- [ ] Filter popover composes with active lens (AND semantics)
- [ ] Deprecated hidden by default; toggle restores (RR-3)
- [ ] No duplicate nodes after reframe (RR-2)
- [ ] `make ci` green

## Dependencies

- PX5-EWO-004 PASS (canvas shell + selection model)

## Forbidden

- Discovery backend API (client-side filter on graph payload)
- Serendipity strip (EWO-007)
- Basket, saved views
- SoR / Constitution / `builder_engine/` changes
