# EWO-7C — Inference Enforcement Layer (Academic Production)

> **Status:** ✅ **Approved** (2026-07-01)  
> **Spawned from:** `.asep/reports/C.6-R2.md`  
> **Category:** Inference Enforcement  
> **Report:** `.asep/reports/EWO-7C-inference-enforcement.md`

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | EWO-7C |
| **Graph node** | `ewo-7c-inference-enforcement` |
| **Depends on** | `ewo-7b-academic-production-path` |
| **Unblocks** | C.6-R3 |

---

## Objective

Strengthen **inference-time enforcement** of academic citation behavior without modifying
OR-6 capability, oracle, or acceptance criteria.

## Architectural framing — Model compliance (5th layer)

| Layer | OR | ThesisOS guarantees |
|-------|-----|---------------------|
| Knowledge | OR-3 | Corpus correct in runtime |
| Policy | OR-4 | Norms available |
| Organizational | OR-5 | Decisions respected |
| Execution | OR-6 | Production under constraint |
| **Model compliance** | OR-6 W-06 | **Induce** author-date — not deterministic |

EWO-7B fixed **production path**. EWO-7C adds **inference enforcement** when the model
ignores explicit instructions.

## Scope

**In:** de-priming, few-shot, output constraints, single deterministic retry guard.  
**Out:** OR-4/6 changes, oracle changes, manual citation post-processing.

## Operator disposition (2026-07-01)

```text
Disposition: C.6-R2 PARTIAL → REJECT
Route: EWO-7C APPROVED
Follow-up: C.6-R3
```
