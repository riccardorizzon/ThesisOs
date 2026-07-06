# Engineering WorkOrder Proposal — PX4-EWO-002

> **Status:** **AUTHORIZED** — `.asep/reports/PX4-AUTHORIZATION-WAVE-1-20260706.md`

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  category: A
  hypothesis_id: n/a
  success_metric: "Concept domain model satisfies ADR-0037 invariants INV-KM-2"
  exit_id: n/a
  program_mode: product
```

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX4-EWO-002 |
| **Title** | Concept domain model |
| **Wave** | px4-parallel/wave_1_foundation |
| **Layer** | Business |

## Objective

Persisted **Concept** entity with M:N source links and typed relations per ADR-0037.

## Deliverables

- `backend/app/models/knowledge.py` — Concept, ConceptSourceLink, ConceptRelation
- Pydantic CRUD schemas in `backend/app/schemas/knowledge.py`
- `backend/app/services/knowledge/repository.py`

## Acceptance

- [x] slug unique per project_id (INV-KM-2)
- [x] relation types: supports, contradicts, extends, used_in, related
- [x] envelope mapping preserves PX-3 API shape
