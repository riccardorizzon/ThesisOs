# Architect Program Review — PX-2 Research Workspace Experience

> Review gate between **Execution Authorization Amendment ratification** and **PX-2 EWO dispatch**.  
> Constitution and META-1 unchanged. PX-1 frozen.

---

## Status

| Field | Value |
|-------|-------|
| **Product spec** | `docs/product/specs/px2-research-workspace-experience.md` |
| **UI spec** | `design-system/thesisos/px2-research-workspace-ui-spec.md` |
| **Authorization amendment** | `docs/product/EXECUTION-AUTHORIZATION-PX2-AMENDMENT.md` — **PROPOSED** |
| **Engineering program** | `.asep/programs/thesisos-product-v2.yaml` |
| **Parallel plan** | `.asep/programs/px2-parallel.yaml` |
| **Review status** | **PASS** — amendment ratified 2026-07-04; Wave A dispatched |

---

## Four questions

| # | Question | PASS | Notes |
|---|----------|------|-------|
| 1 | Scope matches Execution Authorization Amendment (PX-2 only)? | ☑ | Capabilities PX-2.1…2.5; PX-3…6 excluded per amendment |
| 2 | EWOs reference applicable ADRs without amending frozen artifacts? | ☑ | 0036, 0037, 0038, 0039, 0040; no Constitution change |
| 3 | PX-1 qualification surfaces preserved (no retroactive reopen)? | ☑ | EWOs **activate** shells; ownership boundaries explicit |
| 4 | Qualification criteria defined for PX-2? | ☑ | QWO-PX2-001 with 14 AC from spec §24 |

---

## Architecture review summary

| Dimension | Verdict | Notes |
|-----------|---------|-------|
| IA (ADR-0036) | **CONFORM** | No new top-level routes; `/writing/[chapterId]`, `/sources/[sourceId]` activation only |
| Three-panel contract | **CONFORM** | Frozen layout; PX-2 adds behavior not structure |
| Context Engine (ADR-0038) | **EXTEND v0→v1** | Selection-scoped packet assembly; live ContextBar counts |
| AI interaction (ADR-0039) | **CONFORM** | Lateral panel; proposal queue; no silent writes (IR-2) |
| Product state (ADR-0040) | **CONFORM** | Deterministic chapter lifecycle + progress |
| Runtime Constitution C1–C8 | **CONFORM** | Business-layer frontend + existing M6 chapter seam |
| META-1 | **FROZEN** | No new ASEP categories |

### Backend seams (existing, not redesigned)

| Seam | Role in PX-2 |
|------|--------------|
| `GET /projects/{id}/context` | Extend query params for entity/selection scope |
| `backend/app/api/chapters.py` | Autosave, status lifecycle, conflict detection |
| `backend/app/graph/writer.py` | AI actions from Writing panel |
| Memory / proposal services | Session bundle atomic close (OR-7) |

No runtime graph redesign. No new OR milestone.

---

## EWO backlog (approved for proposal)

| EWO | Capability | Wave | Depends on |
|-----|------------|------|------------|
| PX2-EWO-001 | PX-2.1 | A | PX-1 complete |
| PX2-EWO-002 | PX-2.2 | A | PX-1 complete |
| PX2-EWO-005 | PX-2.4 | A | PX2-EWO-001 |
| PX2-EWO-003 | PX-2.2 | B | PX2-EWO-001, PX2-EWO-002 |
| PX2-EWO-004 | PX-2.3 | B | PX2-EWO-002 |
| PX2-EWO-006 | PX-2.5 | B | PX2-EWO-002, PX2-EWO-003 |
| PX2-EWO-007 | PX-2.2/3 | C | PX2-EWO-002, PX2-EWO-003 |
| PX2-EWO-008 | All | D | PX2-EWO-001…007 |
| QWO-PX2-001 | PX-2 | Gate | All PX2-EWO-* |

---

## Verdict

```text
[x] PASS  — EWO proposals + program draft approved for filing
[ ] FAIL  — revise spec or backlog
```

**Dispatch condition:** `EXECUTION-AUTHORIZATION-PX2-AMENDMENT` status → **RATIFIED** + Architect sign-off on this review.

---

## Sign-off

```text
Product Constitution:     v1.0 (Frozen)
META-1:                   FROZEN
PX-1:                     COMPLETE / QUALIFIED (frozen)
Proposed scope:           PX-2 Research Workspace Experience
Excluded:                 PX-3, PX-4, PX-5, PX-6

Architect:                [ pending formal sign-off ]
Engineering Supervisor:   draft review PASS (2026-07-04)
Date:                     2026-07-04
```

---

## WO-TRACE

```text
PX-1 COMPLETE → EXECUTION-AUTHORIZATION-PX2-AMENDMENT (proposed)
  → px2-research-workspace-experience.md
  → ARCHITECT-PROGRAM-REVIEW-PX2.md (this document)
  → PX2-EWO-* proposals → px2-parallel.yaml → QWO-PX2-001
```
