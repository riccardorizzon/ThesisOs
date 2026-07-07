# Engineering WorkOrder Proposal — PX5-EWO-005

> **Status:** **AUTHORIZED** — `.asep/reports/PX5-AUTHORIZATION-WAVE-D-20260707.md`

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  category: A
  hypothesis_id: n/a
  success_metric: "Inspector rail populates for selected concept nodes per UI spec §6"
  exit_id: n/a
  program_mode: product
```

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX5-EWO-005 |
| **Title** | Inspector rail |
| **Milestone** | PX-5 |
| **Wave** | D |
| **Layer** | Business (Product Plane) |

## Objective

Populate the inspector rail (PP-1 tab pattern) for selected concept nodes on the
research canvas.

## Deliverables

- `frontend/components/research/canvas/ResearchInspectorRail.tsx`
- Tabs: Dettaglio · Collegamenti · Azioni (UI spec §6)
- Dettaglio: title, lifecycle badge, confidence, summary snippet from concept envelope
- Collegamenti: linked sources/concepts/chapters as deep links
- Azioni: Apri Explain · Aggiungi al basket (basket action stub until Wave E)
- Multi-select mode: count + batch action stub
- `⌘\` toggle inspector (UI spec §13)
- Unit tests for empty/single/multi states
- `.asep/reports/PX5-EWO-005-inspector-rail.md`

## Acceptance

- [ ] Single concept select populates all three tabs
- [ ] Apri Explain navigates to `/knowledge/[slug]` (KR-13)
- [ ] Collegamenti links resolve to existing routes (sources, graph, writing)
- [ ] Multi-select shows batch summary, not per-node tabs
- [ ] No duplicate concept detail page — inspector is summary only (RR-6)
- [ ] `make ci` green

## Dependencies

- PX5-EWO-004 PASS (canvas shell + selection model)

## Forbidden

- Basket persistence, saved views
- New backend endpoints (reuse concept detail/header APIs)
- SoR / Constitution / `builder_engine/` changes
