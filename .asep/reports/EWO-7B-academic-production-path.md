# EWO-7B — Academic Production Path Report

**Date:** 2026-07-01  
**WorkOrder:** EWO-7B · **Category:** Production Path  
**Spawned from:** C.6-R1 PARTIAL (W-06) · operator REJECT disposition  
**Verdict:** **PASS**

---

## Objective

Enforce author-date citation discipline in the academic production path so OR-6 W-06
passes without weakening OR-4 normative invariants.

---

## Changes

| Component | Change |
|-----------|--------|
| `backend/app/graph/academic_production.py` | **New** — academic turn detection, author/year hints, citation blocks |
| `backend/app/graph/prompt_wire.py` | Academic mode → author-date instructions + source headers |
| `backend/app/graph/orchestration/writer_prompt.py` | Writer always author-date; academic grounding headers |
| `backend/tests/test_academic_production.py` | Regression + OR-6 prompt coverage |
| `ewo7b_academic_production_path.py` | Audit script |

**No** Ground Truth edits · **no** QWO execution.

---

## Root cause (confirmed)

C.6-R1 output used `[2]` because both conversation grounding and writer system prompts
explicitly requested `bracketed numbers like [1], [2]`. Content, A/B, and traceability
were correct — failure was **systemic prompt default**, not model variance.

---

## Verification

| Check | Result |
|-------|--------|
| OR-6 canonical prompt → `is_academic_writing_query` | ✅ |
| Academic grounding → author-date instruction | ✅ |
| Academic grounding → forbids numeric `[n]` in prose | ✅ |
| Source header → `Albers (1963)` | ✅ |
| Corpus-list query → numeric mode preserved | ✅ |
| Writer `WRITER_SYSTEM` → author-date | ✅ |
| Unit tests | `test_academic_production.py` green |

---

## Success criteria (operator)

| Criterion | Status |
|-----------|--------|
| Eliminate numeric `[n]` instruction in academic path | ✅ |
| Author-date as default for academic/writer production | ✅ |
| No regression C.6.1 / C.6.2 / C.6.4 design | ✅ (prompt-only; sub-capabilities unchanged) |

---

## Lifecycle

| Field | Value |
|-------|-------|
| `ewo-7b-academic-production-path` | **`implemented`** |
| `or-6-write-paragraph` | **`approved`** — ready for **C.6-R2** |
| Unblocks | **C.6-R2** re-QWO |

**Backend restart required** after deploy before C.6-R2.

---

## WO-TRACE

```text
C.6-R1 PARTIAL (W-06) → REJECT → EWO-7B Production Path → audit PASS → C.6-R2
```
