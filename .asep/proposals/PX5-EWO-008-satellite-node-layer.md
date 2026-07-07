# Engineering WorkOrder Proposal — PX5-EWO-008

> **Status:** **AUTHORIZED** — `.asep/reports/PX5-AUTHORIZATION-INTEGRATION-E-20260707.md`

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  category: A
  hypothesis_id: n/a
  success_metric: "Canvas graph returns concept + satellite nodes per px5-research-experience-v1.md §4.1"
  exit_id: n/a
  program_mode: product
```

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX5-EWO-008 |
| **Title** | Satellite node layer |
| **Milestone** | PX-5 |
| **Wave** | E |
| **Layer** | Business (Product Plane) |

## Objective

Extend the knowledge graph API with `profile=canvas` to include linked satellite
nodes (source, author, decision, chapter) and render distinct shapes on the canvas
viewport.

## Deliverables

- Backend schema: `kind` on nodes; `link_kind` on edges; canvas limits 80/150/300
- `build_canvas_graph` enrichment in `backend/app/services/knowledge/graph.py`
- API query param `profile=canvas` on `/knowledge/graph`
- Frontend types, layout, viewport rendering per node kind
- Canvas route uses canvas profile
- Tests + `.asep/reports/PX5-EWO-008-satellite-node-layer.md`

## Dependencies

- PX5-INTEGRATION-D PASS

## Forbidden

- Basket persistence, saved views (EWO-009/010)
- Minimap/cluster modal (EWO-011)
- SoR / Constitution / `builder_engine/` changes
