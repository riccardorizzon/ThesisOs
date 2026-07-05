# EWO-4A — Corpus-list Grounding Remediation Report

**Date:** 2026-06-30  
**WorkOrder:** EWO-4A · **Category:** Grounding  
**Spawned from:** `.asep/reports/C.3-R3-disposition.md`  
**Verdict:** **PASS**

---

## Objective

Stabilize canonical corpus recovery for OR-3 query — retrieval boost + FOND/SUPPORTO/PERIFERICO grounding.

---

## Changes

| Component | Change |
|-----------|--------|
| `backend/app/graph/corpus_query.py` | Shared OR-3 query detection + boost queries |
| `backend/app/graph/retriever.py` | Corpus-list + exclusion merge; limit 12 for corpus queries |
| `backend/app/graph/prompt_wire.py` | A.1/A.2/A.3 taxonomy instruction on corpus queries |
| `ewo4a_corpus_list_grounding.py` | OR-3 merged-retrieval audit script |

**No** Ground Truth · corpus · thesis edits.

---

## Audit (OR-3 canonical query)

| Check | Result |
|-------|--------|
| `/health` | 200 OK |
| Bibliography-Master in merged top-12 | ✅ |
| Eco in merged context | ✅ |
| Flügel in merged context | ✅ |
| Exclusion markers | ✅ |
| FOND/SUPPORTO taxonomy markers | ✅ |
| Unit tests (grounding + retriever) | 11 passed |

---

## Cognitive pipeline

```text
Ground Truth   ✅
Retrieval      ✅  (EWO-4A corpus-list boost)
Grounding      ✅  (EWO-4 exclusions + EWO-4A taxonomy)
Reasoning      →  validated by C.3-R4
```

---

## Lifecycle

| Field | Value |
|-------|-------|
| `ewo-4a-corpus-list-grounding` | **`implemented`** |
| Unblocks | **C.3-R4** re-QWO |

**Backend restart required** after deploy — completed 2026-06-30.

---

## WO-TRACE

```text
C.3-R3 PARTIAL REJECTED → EWO-4A Grounding → audit PASS → C.3-R4
```
