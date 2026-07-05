# EWO-7C — Inference Enforcement Layer Report

**Date:** 2026-07-01  
**WorkOrder:** EWO-7C · **Category:** Inference Enforcement  
**Spawned from:** C.6-R2 PARTIAL (prompt verified; W-06 model non-compliance)  
**Verdict:** **PASS**

---

## Objective

Add inference-time enforcement for academic author-date citations without changing OR-6
capability definition, oracle, or acceptance criteria.

---

## Changes

| Component | Change |
|-----------|--------|
| `backend/app/graph/academic_production.py` | De-primed preamble, few-shot, enforcement block, retry detectors |
| `backend/app/graph/inference_enforcement.py` | **New** — buffered generate + one deterministic retry |
| `backend/app/graph/prompt_wire.py` | Academic grounding uses EWO-7C blocks |
| `backend/app/graph/orchestration/writer_prompt.py` | Few-shot + enforcement in writer system |
| `backend/app/graph/conversation.py` | Academic turns → enforcement layer |
| `backend/app/graph/writer.py` | Writer route → enforcement layer |
| `docs/asep-capability-model.md` | §4D Model compliance |
| `backend/tests/test_inference_enforcement.py` | Retry guard unit tests |

**No** Ground Truth edits · **no** oracle changes · **no** post-hoc citation rewriting.

---

## Enforcement mechanics

1. **De-priming:** academic grounding no longer says "numbered sources".
2. **Few-shot:** correct `(Albers, 1963)` vs wrong `[2]` example inline.
3. **Output constraints:** mandatory author-date; forbidden `[n]` in prose.
4. **Retry guard (deterministic):** if academic output has `[n]` and no author-date →
   exactly **one** retry with fixed `CITATION_ENFORCEMENT_RETRY_MESSAGE`; first pass
   buffered (not streamed); retry output streamed.

---

## Verification

| Check | Result |
|-------|--------|
| Unit tests academic + inference + writer + grounding | 29 passed |
| Retry fires on `[2]` without author-date | ✅ |
| No retry when `(Albers, 1963)` present | ✅ |
| Numeric Q&A mode unchanged | ✅ |

---

## Model compliance note (framework lesson)

If C.6-R3 still fails W-06 after enforcement, classify as **model non-compliance** —
not OR-6 mis-design. ThesisOS guarantees instruction + enforcement; not LLM determinism.

---

## Lifecycle

| Field | Value |
|-------|-------|
| `ewo-7c-inference-enforcement` | **`implemented`** |
| Unblocks | **C.6-R3** re-QWO |

**Backend restart required** before C.6-R3.

---

## WO-TRACE

```text
C.6-R2 PARTIAL (model) → EWO-7C Inference Enforcement → audit PASS → C.6-R3
```
