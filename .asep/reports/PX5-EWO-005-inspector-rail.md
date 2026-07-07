# PX5-EWO-005 — Inspector rail

> **WorkOrder:** PX5-EWO-005  
> **Wave:** D  
> **Status:** **PASS**  
> **Date:** 2026-07-07  
> **Layer:** Business (Product Plane)

---

## Deliverables

| Artifact | Path | Status |
|----------|------|--------|
| Inspector rail | `frontend/components/research/canvas/ResearchInspectorRail.tsx` | **PASS** |
| Shell integration | `ResearchCanvasShell.tsx` | **PASS** |
| Unit tests | `ResearchInspectorRail.test.tsx` | **PASS** |

---

## Acceptance

| Criterion | Result |
|-----------|--------|
| Single select → Dettaglio / Collegamenti / Azioni | **PASS** |
| Apri Explain → `/knowledge/[slug]` | **PASS** |
| Collegamenti deep links | **PASS** |
| Multi-select batch summary | **PASS** |
| Summary only (RR-6) | **PASS** |
| `⌘\` toggle inspector | **PASS** |
| `make ci` green | **PASS** |

---

```text
Milestone Status: PASS
Recommended Next Action: PX5-EWO-007 serendipity + integration
```
