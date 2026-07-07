# PX5-EWO-001 — Research Experience Spec + UX foundation

> **WorkOrder:** PX5-EWO-001  
> **Wave:** A — Spec foundation  
> **Status:** **PASS**  
> **Authorization:** `.asep/reports/PX5-AUTHORIZATION-20260706.md`  
> **Date:** 2026-07-06  
> **Layer:** Business (spec-only — no product code)

---

## Deliverables

| Artifact | Path | Status |
|----------|------|--------|
| Product spec v1 | `docs/product/specs/px5-research-experience-v1.md` | **PASS** |
| UI spec draft | `design-system/thesisos/px5-research-experience-ui-spec.md` | **PASS** |
| EWO report | this document | **PASS** |

---

## Acceptance criteria

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Canvas scope, discovery, node semantics, Writing handoff | **PASS** | Product §2, §4–§8 |
| UI layout, interaction, limits distinct from PX-3 §10 | **PASS** | UI §4–§5, §10; Product §5.2 |
| Boundary table PX-3 / PX-4 / PX-5 | **PASS** | Product §3 |
| INV-KM-5 preserved | **PASS** | Product §1, §4; nodes from PX-4 store only |
| No implementation code | **PASS** | Spec-only EWO |

---

## Boundary verification

| Surface | Route | Owner | PX-5 spec respects |
|---------|-------|-------|---------------------|
| Guided trail | `/research/guided` | PX-3.10 | ✓ Hub links only; no trail impl |
| Navigation graph | `/knowledge/graph` | PX-3/PX-4 | ✓ Cross-link §10; limits unchanged |
| Explain Page | `/knowledge/[slug]` | PX-4 | ✓ RR-6 / KR-13 |
| Spatial canvas | `/research/canvas` | **PX-5** | ✓ Primary deliverable |

---

## Capability coverage

| ID | Spec section | UI section |
|----|--------------|------------|
| PX-5.1 Spatial Canvas | §5 | §4–§5 |
| PX-5.2 Discovery Lenses | §6 | §7 |
| PX-5.3 Serendipity Paths | §7 | §8 |
| PX-5.4 Canvas Selection | §5.4 | §5.3, §6 |
| PX-5.5 Saved Views | §9 | §11 |
| PX-5.6 Cross-Module Navigation | §10 | §6 |

---

## Qualification draft

QWO-PX5-001 acceptance criteria drafted in product §16 (AC-1…AC-10).

---

## Regression

| Check | Result |
|-------|--------|
| `make ci` | Not required for spec-only EWO |
| SoR / Constitution / builder_engine | Unchanged ✓ |

---

## STOP — Architect ratification

Spec artifacts ready for Architect sign-off before Wave B implementation authorization.

Recommended spawn order:

1. `PX5-EWO-002` — Research hub + route scaffolding  
2. `PX5-EWO-003` — Canvas viewport + node layer  
3. Parallel program `.asep/programs/px5-parallel.yaml`

---

## WO-TRACE

```text
AUTHORIZE PX-5 → PX5-EWO-001 PASS (this report)
  → Architect ratification → Wave B authorization → implementation EWOs
```

---

```text
Milestone Status: PASS
Repository Status: main @ d5206a0f
Remaining Scope: PX5-EWO-002+ implementation (blocked until wave authorization)
Known Risks: `/research/guided` (PX-3.10) not yet implemented — hub links to stub
Recommended Next Action: Architect ratify spec → AUTHORIZE PX-5 Wave B
```
