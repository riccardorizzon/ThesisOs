# Engineering WorkOrder Proposal — PX4-EWO-003

> **Status:** **AUTHORIZED** — `.asep/reports/PX4-AUTHORIZATION-WAVE-1-20260706.md`

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  category: A
  hypothesis_id: n/a
  success_metric: "Concept CRUD API satisfies ADR-0037 compliance C1"
  exit_id: n/a
  program_mode: product
```

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX4-EWO-003 |
| **Title** | Concept CRUD API |
| **Wave** | px4-parallel/wave_1_foundation |
| **Layer** | Business |

## Objective

POST/PATCH/DELETE concept endpoints; async service with catalog fallback for read.

## Deliverables

- `backend/app/api/knowledge.py` — CRUD routes
- `backend/app/services/knowledge/service.py` — async read + write
- `backend/tests/test_knowledge_crud.py`

## Acceptance

- [x] POST 201 / PATCH 200 / DELETE 204
- [x] 409 on duplicate slug
- [x] PX-3 read endpoints unchanged (catalog fallback when DB empty)
