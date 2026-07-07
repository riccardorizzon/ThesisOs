# Engineering WorkOrder Proposal — PX5-EWO-002

> **Status:** **AUTHORIZED** — `.asep/reports/PX5-AUTHORIZATION-20260707.md`

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  category: A
  hypothesis_id: n/a
  success_metric: "Research hub and canvas routes wired per px5-research-experience-v1.md §3"
  exit_id: n/a
  program_mode: product
```

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX5-EWO-002 |
| **Title** | Research hub + route scaffolding |
| **Milestone** | PX-5 |
| **Layer** | Business (Product Plane) |

## Objective

Replace PX-1 `ModuleStub` on research routes with the **Research hub** entry point
and wire `/research/canvas`, `/research/guided`, and concept-focus redirect per
product spec §3 and UI spec §2–§3.

## Deliverables

- `frontend/components/research/ResearchHubPage.tsx`
- `frontend/app/research/page.tsx` — hub
- `frontend/app/research/canvas/page.tsx` — canvas stub
- `frontend/app/research/guided/page.tsx` — guided stub (PX-3.10 placeholder)
- `frontend/app/research/[conceptId]/page.tsx` — redirect to canvas focus
- `frontend/lib/routes.ts` + tests
- `.asep/reports/PX5-EWO-002-research-hub-scaffolding.md`

## Acceptance

- [ ] `/research` hub with canvas + guided links (UI spec §3)
- [ ] `/research/canvas` route stub wired
- [ ] `/research/[conceptId]` redirect to canvas focus
- [ ] `ModuleStub` replaced on research routes
- [ ] `make ci` green

## Dependencies

- PX5-EWO-001 PASS (spec ratified)
- PX-4 concept list API (fallback stub when API unavailable)

## Forbidden

- Canvas rendering, discovery lenses, or saved views persistence
- Modifying PX-3 guided research semantics beyond stub link
- SoR / Constitution / `builder_engine/` changes
