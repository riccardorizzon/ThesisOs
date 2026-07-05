# PX3-EWO-001 — Knowledge Object Foundation

> **WorkOrder:** PX3-EWO-001  
> **Milestone:** PX-3 Knowledge Experience (Conformance Program)  
> **Authorization:** `.asep/reports/PX3-AUTHORIZATION-20260705.md`  
> **Verdict:** **IMPLEMENTED**

---

## Summary

Established the Knowledge Object substrate for PX-3 Wave A: backend envelope schema
and read API, frontend shared types and `KnowledgeObjectCard`, lifecycle/confidence
badges (PP-4/PP-5), and ADR-0036 `/documents/*` → `/sources/*` redirects.

---

## Deliverables

| Artifact | Path |
|----------|------|
| Envelope schema | `backend/app/schemas/knowledge.py` |
| Catalog + service | `backend/app/services/knowledge/` |
| Knowledge API | `backend/app/api/knowledge.py` |
| Frontend types | `frontend/lib/knowledgeTypes.ts` |
| API client | `frontend/lib/knowledgeClient.ts` |
| Shared card | `frontend/components/knowledge/shared/` |
| Route migration | `frontend/lib/routes.ts` (documents redirects) |

---

## Acceptance

| Criterion | Status |
|-----------|--------|
| Knowledge envelope schema via API (concepts + sources) | PASS |
| Lifecycle + confidence map to spec §4 badges | PASS |
| Shared KnowledgeObjectCard (PP-09) | PASS |
| `/documents/*` → `/sources/*` redirect | PASS |
| PX-2 cite/reader unchanged | PASS (no PX-2 file edits) |
| Tests | PASS — `test_knowledge_api.py`, `KnowledgeObjectCard.test.tsx` |

---

## Conformance

No deviations recorded — Conformance Log unchanged.

---

## Unblocks

- **PX3-EWO-002** Sources Module Enrichment (parallel-ready after merge)
- **PX3-EWO-003** Knowledge Explorer (parallel-ready after merge)

---

## WO-TRACE

```text
AUTHORIZE PX-3 → PX3-EWO-001 IMPLEMENTED → PX3-EWO-002 ∥ PX3-EWO-003 → PX3-EWO-004
```
