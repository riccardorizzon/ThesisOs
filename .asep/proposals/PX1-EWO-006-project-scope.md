# Engineering WorkOrder Proposal — PX1-EWO-006

> **Status:** APPROVED (scope extended 2026-07-03)

Program: `.asep/programs/thesisos-product-v2.yaml`  
Capability: `px1-ewo-006-project-scope`

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX1-EWO-006 |
| **Type** | EWO (Infrastructure) |
| **Milestone** | PX-1 Foundation |
| **Depends on** | PX1-EWO-001, PX1-EWO-005 |
| **ADR refs** | ADR-0040 |

---

## Objective

Introduce **Project Context** (not just `project_id`) so the API is ready for
multi-product ASEP hosting (ThesisOS, ContractOS, ResearchOS).

---

## Ownership (exclusive — Sub-agent A)

```text
backend/app/schemas/context.py          # ProjectContext fields
backend/app/api/projects.py
backend/app/services/context/           # project resolution stub
frontend/lib/projectContext.ts          # NEW
frontend/lib/contextClient.ts
frontend/lib/contextLoad.ts
```

**Must NOT touch:** `frontend/components/**`, `frontend/app/**`

---

## Scope

### ProjectContext (minimum)

```typescript
{
  project_id: string      // default: thesis-agent
  product_id: string      // default: thesisos
  workspace_id?: string   // optional tenant workspace
  session_id?: string    // optional operator session
}
```

### In scope

- ProjectContext echoed in `GET /projects/{id}/context` response
- Query params: `product_id`, `workspace_id`, `session_id`
- Default project from promoted thesis-agent template
- Frontend context client passes ProjectContext
- Session/project resolution stub for Writing + Home routes

### Out of scope

- Full auth/session middleware — PX-2+
- ContractOS / ResearchOS product shells — future programs

---

## Acceptance Criteria

- [ ] ProjectContext in API request/response
- [ ] Defaults: `project_id=thesis-agent`, `product_id=thesisos`
- [ ] Frontend routes use shared project context helper
- [ ] Tests + `make ci` green

---

## WO-TRACE

```text
PX1-EWO-005 (Context Graph + presentation hint) → PX1-EWO-006 → QWO-PX1-001
```
