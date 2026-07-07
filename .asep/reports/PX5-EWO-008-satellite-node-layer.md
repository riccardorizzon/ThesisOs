# PX5-EWO-008 — Satellite node layer

> **WorkOrder:** PX5-EWO-008  
> **Wave:** E  
> **Verdict:** **PASS**  
> **Date:** 2026-07-07  
> **Authorization:** `.asep/reports/PX5-AUTHORIZATION-INTEGRATION-E-20260707.md`

---

## Deliverables

| Artifact | Status |
|----------|--------|
| `backend/app/schemas/knowledge_graph.py` — `kind`, `link_kind`, canvas limits | PASS |
| `backend/app/services/knowledge/graph.py` — canvas satellite enrichment | PASS |
| `backend/app/api/knowledge.py` — `profile=canvas` query param | PASS |
| `frontend/lib/knowledgeTypes.ts` — canvas node/edge types | PASS |
| `frontend/lib/canvasLayout.ts` — satellite orbit layout | PASS |
| `frontend/components/research/canvas/ResearchCanvasViewport.tsx` — per-kind shapes | PASS |
| `frontend/lib/canvasLenses.ts` — preserve satellites on lens filter | PASS |
| `frontend/app/research/canvas/page.tsx` — canvas profile fetch | PASS |
| Tests (backend + `canvasLayout.test.ts`) | PASS |

---

## Acceptance

| Criterion | Result |
|-----------|--------|
| `/knowledge/graph?profile=canvas&depth=2` returns concept + source satellites | PASS |
| Author/decision/chapter stubs when linked to visible concepts | PASS |
| Distinct viewport shapes per `kind` | PASS |
| Concept double-click → Explain; source → Source reader | PASS |
| PX-3 default graph unchanged (no `profile=canvas`) | PASS |
| `make ci` green | PASS |

---

## Notes

- Decision/chapter satellites use catalog stubs until DB links exist (Wave E follow-up).
- Basket (EWO-009) and saved views (EWO-010) remain deferred.

---

## WO-TRACE

```text
AUTHORIZE Integration E → PX5-EWO-008 PASS (this report)
  → PX5-EWO-009 ∥ PX5-EWO-010 → PX5-EWO-011 → PX5-INTEGRATION-E
```
