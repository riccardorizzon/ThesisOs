# PX3-EWO-003 — Knowledge Explorer

> **Verdict:** **IMPLEMENTED**  
> **Report:** `.asep/reports/PX3-EWO-003-knowledge-explorer.md`

## Deliverables

- `frontend/components/knowledge/explorer/` (Explorer, Filters, ConceptCard)
- `/knowledge` page wired to Knowledge API
- Featured anchor concept (STIGMATA)
- Filters: stato, core, confidenza, mostra candidati

## Acceptance: PASS

- Concept cards with lifecycle + confidence badges
- Deprecated hidden by default; candidate toggle works
- Apri → `/knowledge/{slug}`; Grafo deferred stub
- Source count links → `/sources`
