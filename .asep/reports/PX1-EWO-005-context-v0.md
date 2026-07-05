# PX1-EWO-005 — Context Engine v0

**WorkOrder:** PX1-EWO-005  
**Date:** 2026-07-03  
**Verdict:** **IMPLEMENTED**

---

## Deliverables

| Artifact | Path |
|----------|------|
| Context schemas | `backend/app/schemas/context.py` |
| Context service | `backend/app/services/context/service.py` |
| Projects API | `backend/app/api/projects.py` |
| Backend tests | `backend/tests/test_context_api.py` |
| Context client | `frontend/lib/contextClient.ts` |
| Context loader | `frontend/lib/contextLoad.ts` |
| ContextBar | `frontend/components/ContextBar.tsx` |
| Writing integration | `frontend/app/writing/page.tsx`, `writing/[chapterId]/page.tsx` |
| Frontend tests | `frontend/components/ContextBar.test.tsx` |

---

## Acceptance Criteria

| Criterion | Result |
|-----------|--------|
| GET /projects/{id}/context returns ContextPacket subset | **PASS** |
| Precedence binding decisions + entity + corpus_constraints | **PASS** |
| ContextBar on Writing stub route | **PASS** |
| Tests + build | **PASS** |

---

## API

```text
GET /projects/thesis-agent/context?surface=writing&entity_type=chapter&entity_id={id}
```

Returns `schema_version`, `project`, `decisions`, `corpus_constraints`, `writing_rules` (when surface=writing), optional `entity`, empty PX-4+ arrays.

Default project id: `thesis-agent` (full scope in PX1-EWO-006).

### Post-review evolution (2026-07-03)

- **Context Graph** assembly: Decisions → Constraints → Knowledge → Workspace → Session → User Intent
- **`surface`** demoted to `presentation` hint — does not drive assembly
- **`ProjectContext`** schema introduced (`project_id`, `product_id`, `workspace_id`, `session_id`)
- Schema version bumped to `0.2`
- CI baseline restored (`test_m5_graph_topology` — corpus multi-search separated from branch routing test)

---

## Next Ready

| ID | Title |
|----|-------|
| **PX1-EWO-006** | Project scope scaffolding |
| QWO-PX1-001 | PX-1 qualification (blocked until EWO-005/006) |

---

## WO-TRACE

```text
PX1-EWO-004 → PX1-EWO-005 → PX1-EWO-006
```
