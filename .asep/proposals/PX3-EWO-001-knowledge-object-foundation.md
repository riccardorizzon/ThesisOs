# Engineering WorkOrder Proposal — PX3-EWO-001

> **Status:** ✅ **IMPLEMENTED** — PX3-AUTHORIZATION-20260705
>
> Program: `.asep/programs/thesisos-product-v2.yaml`  
> Wave: `px3-parallel/wave_a_foundation`  
> Spec: `docs/product/specs/px3-knowledge-experience-v2.md` §3, §4, §6  
> UI: `design-system/thesisos/product-patterns.md` PP-09

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX3-EWO-001 |
| **Sub-agent** | A |
| **Type** | **EWO** — Infrastructure |
| **EWO category** | **Infrastructure** |
| **Capability** | `px3-ewo-001-knowledge-object-foundation` |
| **Milestone** | PX-3 Knowledge Experience |
| **Layer** | Business (Product Plane) |
| **Lifecycle transition** | `approved` → `implemented` (on success) |

---

## Objective

Establish the **Knowledge Object Model** substrate shared by all PX-3 surfaces:
backend schemas/API, frontend envelope types and shared components, lifecycle state
mapping, and legacy route migration per ADR-0036.

---

## Ownership (exclusive)

```text
backend/app/schemas/knowledge.py
backend/app/api/knowledge.py
backend/app/services/knowledge/**
frontend/lib/knowledgeTypes.ts
frontend/lib/knowledgeClient.ts
frontend/components/knowledge/shared/**
frontend/app/documents/**          (redirect only)
frontend/middleware.ts             (redirect rules only)
```

**Forbidden:** `components/sources/**` (EWO-002), `components/knowledge/explorer/**` (EWO-003),
Explain Page, graph, reader enrichment, annotation persistence.

---

## Scope

### In scope

1. **Shared envelope schema** — id, slug, type, title, subtitle, summary, confidence,
   knowledge_state, linked_* counts per spec §3.1
2. **Lifecycle states** — Candidate · Validated · Linked · Referenced · Deprecated (§4)
3. **Knowledge API** — list/get envelope for concepts and sources (read-only; corpus-backed)
4. **Frontend envelope** — `KnowledgeObjectCard`, lifecycle badges, confidence chip (PP-09)
5. **Route migration** — `/documents/*` → `/sources/*` redirect (ADR-0036 legacy table)
6. **Type specialization stubs** — concept | source enums; no full Explain/reader UI

### Out of scope

- Enriched Sources list UI (PX3-EWO-002)
- Knowledge Explorer page (PX3-EWO-003)
- Semantic search ranking (partial in 002)
- Annotation/citation persistence
- Full source import / PDF parse
- Engineering Runtime / `builder_engine/`

---

## Constraints

- Product Constitution v1.0 + ADR-0037 (concepts canonical)
- ADR-0036 INV-IA-1 — no new top-level nav items
- MB2 SoR read-only — conformance program
- PX-2 surfaces unchanged in behavior
- Runtime Constitution C1–C8

---

## Acceptance Criteria

- [ ] Knowledge envelope schema exposed via API for concepts and sources
- [ ] Lifecycle + confidence fields map to spec §4 UX badges
- [ ] Shared `KnowledgeObjectCard` renders envelope fields per PP-09
- [ ] `/documents/*` requests redirect to `/sources/*` (301 or Next redirect)
- [ ] PX-2 Sources reader and Writing cite flow unchanged
- [ ] `make ci` green; OR-1…OR-7 regression preserved

---

## Dependencies

| Depends on | Status |
|------------|--------|
| PX-2 frozen | required |
| MB2 SoR 2026-07-05 | required |

**Unblocks:** PX3-EWO-002, PX3-EWO-003

---

## WO-TRACE

```text
AUTHORIZE PX-3 → PX3-EWO-001 → PX3-EWO-002 ∥ PX3-EWO-003 → PX3-EWO-004
```
