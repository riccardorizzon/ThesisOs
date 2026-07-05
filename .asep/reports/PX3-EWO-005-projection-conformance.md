# PX3-EWO-005 — Projection Conformance

> **WorkOrder:** PX3-EWO-005  
> **Wave:** B — Projection Conformance  
> **Status:** **PASS**  
> **Authorization:** `.asep/reports/PX3-AUTHORIZATION-EWO-005-20260705.md`  
> **Date:** 2026-07-05

---

## Conformance contract (evidence)

```yaml
covers:
  sor_sections:
    - "§9 Projection"
  invariants:
    - INV-R-11
  mb2_gates:
    - MB2-Q5
  px3_exercisability: Yes
  class: A
```

---

## Primary objective — Projection Conformance (§9)

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Schema v1 projection | **PASS** | `GET /projects/{id}/conformance/projection` returns SoR §9.1 fields |
| Read-only (INV-R-11) | **PASS** | GET-only endpoint; no mutation routes; artifact labeled non-authoritative |
| Deterministic rebuild (MB2-Q5) | **PASS** | `build_px3_projection()` from Program Graph + `px3-parallel.yaml`; test excludes `derived_at` |
| Snapshot artifact | **PASS** | `.asep/reports/PX3-PROJECTION-SNAPSHOT-20260705.yaml` |

**Rebuild procedure:** `backend/app/services/conformance/projection.py` reads
`.asep/programs/thesisos-product-v2.yaml` (all `*_workorder_backlog` lists) and
`.asep/programs/px3-parallel.yaml`. Same inputs → identical projection (except `derived_at`).

---

## Secondary objective — Explain Page shell (regions A–B)

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Route `/knowledge/[conceptSlug]` | **PASS** | `frontend/app/knowledge/[conceptSlug]/page.tsx` |
| Region A header | **PASS** | `ExplainHeaderBar` — title, badges |
| Region B definition | **PASS** | `ExplainDefinitionBlock` — definition or empty state |
| Page states §9.16 | **PASS** | loading skeleton, ready, not-found |
| Explorer → Explain | **PASS** | Existing explorer links use slug (unchanged) |
| Projection consumer | **PASS** | Read-only wave status from projection API (no dispatch) |

**Out of scope (deferred):** regions C–L, full graph, Supervisor Runtime.

---

## Tests

| Suite | Result |
|-------|--------|
| `backend/tests/test_projection_conformance.py` | **11/11 PASS** (6 new + 5 knowledge) |
| `frontend/.../ExplainPageShell.test.tsx` | **2/2 PASS** |

---

## Conformance Log

**No entries.** N-class: **0**.

---

## Coverage delta

| SoR row | Before | After |
|---------|--------|-------|
| §9 Projection model | ❌ | **✅** |
| §4.5 Projection document | ⏳ | **✅** |

Matrix updated: `.asep/reports/MB2-CONFORMANCE-COVERAGE.md`

---

## Files touched (product)

```text
backend/app/schemas/projection.py
backend/app/schemas/knowledge.py          (ConceptDetailEnvelope)
backend/app/services/conformance/projection.py
backend/app/api/conformance.py
backend/app/api/knowledge.py              (concepts/{slug})
backend/app/main.py
backend/pyproject.toml                    (pyyaml)
backend/tests/test_projection_conformance.py
frontend/app/knowledge/[conceptSlug]/page.tsx
frontend/components/knowledge/explain/**
frontend/lib/knowledgeClient.ts
frontend/lib/knowledgeTypes.ts
.asep/reports/PX3-PROJECTION-SNAPSHOT-20260705.yaml
```

---

## Architect gate — STOP

```text
PX3-EWO-005 PASS — STOP

Await Architect review before authorizing PX3-EWO-006.
PX3-EWO-006 remains NOT authorized for dispatch.
```

---

## WO-TRACE

```text
AUTHORIZE EWO-005 → implement → PASS → STOP (Architect review)
```
