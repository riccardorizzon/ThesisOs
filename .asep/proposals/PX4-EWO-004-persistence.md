# Engineering WorkOrder Proposal — PX4-EWO-004

> **Status:** **AUTHORIZED** — `.asep/reports/PX4-AUTHORIZATION-WAVE-1-20260706.md`

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  category: A
  hypothesis_id: n/a
  success_metric: "Migration 0006 applies; seed preserves PX-3 catalog concepts"
  exit_id: n/a
  program_mode: product
```

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX4-EWO-004 |
| **Title** | Concept persistence |
| **Wave** | px4-parallel/wave_1_foundation |
| **Layer** | Infrastructure |

## Objective

Alembic migration for concept tables, indexes, and seed from PX-3 CONCEPT_CATALOG.

## Deliverables

- `backend/migrations/versions/0006_knowledge_concepts.py`
- Indexes: project+state, project+title, source_slug, relation endpoints

## Acceptance

- [x] Additive migration (0005 → 0006)
- [x] Seed 7 thesis-agent concepts + source links
- [x] Downgrade drops tables cleanly
