# Engineering WorkOrder Proposal — PX5-EWO-003

> **Status:** **AUTHORIZED** — `.asep/reports/PX5-AUTHORIZATION-WAVE-C-20260707.md`

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  category: A
  hypothesis_id: n/a
  success_metric: "Pan/zoom canvas viewport renders concept nodes and edges per px5-research-experience-v1.md §5"
  exit_id: n/a
  program_mode: product
```

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX5-EWO-003 |
| **Title** | Canvas viewport + node layer |
| **Milestone** | PX-5 |
| **Wave** | C |
| **Layer** | Business (Product Plane) |

## Objective

Replace the Wave B canvas stub with a **spatial viewport** — pan/zoom infinite canvas,
concept node layer, and typed edges — wired to the Knowledge graph API at depth 2 per
product spec §5.1–§5.2 and UI spec §4–§5.

## Deliverables

- `frontend/lib/canvasLayout.ts` — radial layout + focus centering
- `frontend/lib/researchCanvasStub.ts` — dev fallback graph
- `frontend/components/research/canvas/ResearchCanvasViewport.tsx` — pan/zoom + SVG layer
- `frontend/components/research/ResearchCanvasPage.tsx` — canvas shell header
- `frontend/app/research/canvas/page.tsx` — fetch graph depth 2, render page
- `frontend/components/research/canvas/ResearchCanvasViewport.test.tsx`
- `.asep/reports/PX5-EWO-003-canvas-viewport-node-layer.md`

## Acceptance

- [ ] `/research/canvas` renders pan/zoom viewport (not dashed stub)
- [ ] Concept nodes: circle 48px / 64px core; lifecycle badge; focus highlight
- [ ] Edges rendered with relation-type stroke (supports/contradicts/extends/related)
- [ ] `?focus={slug}` centers viewport on concept
- [ ] Performance banner when `limits.show_performance_banner`
- [ ] Viewport culling — off-screen nodes omitted from DOM
- [ ] `make ci` green

## Dependencies

- PX5-EWO-002 PASS (route scaffolding)
- PX-4 knowledge graph API (`getKnowledgeGraph`)

## Forbidden

- Lens rail, inspector rail, serendipity strip, saved views persistence
- Discovery API, basket drawer, Writing handoff
- Satellite node kinds (source/author/decision/chapter) — deferred Wave D+
- SoR / Constitution / `builder_engine/` changes
