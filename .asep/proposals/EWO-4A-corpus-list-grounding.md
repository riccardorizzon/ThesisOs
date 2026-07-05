# Engineering WorkOrder Proposal — EWO-4A

> **Status:** ✅ **APPROVED + IMPLEMENTED** (2026-06-30) — report `.asep/reports/EWO-4A-corpus-list-grounding.md`  
> **Spawned from:** `.asep/reports/C.3-R3-disposition.md` (C.3-R3 PARTIAL REJECTED)  
> **EWO category:** **Grounding** (remediation — corpus-list retrieval)  
> **Parent:** EWO-4 (exclusion grounding)  
> Program: `.asep/programs/thesis-agent-migration.yaml`

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | EWO-4A |
| **Type** | EWO |
| **EWO category** | **Grounding** |
| **Capability** | `ewo-4a-corpus-list-grounding` |
| **Blocks** | re-QWO C.3-R4 until implemented + audit PASS |

---

## Objective

Stabilize canonical corpus recovery for the OR-3 query — retrieval + role taxonomy
grounding without Ground Truth or promotion changes.

---

## Evidence

| Finding | Class |
|---------|-------|
| Bibliography-Master absent from OR-3 query top-10 (raw search) | Retrieval Gap |
| Eco / Flügel missing in C.3-R3 output | Retrieval + Reasoning |
| FOND/SUPPORTO mis-labels | Reasoning (prompt taxonomy) |
| Exclusions CORPUS-02/03 | ✅ Fixed by EWO-4 |

**NOT** Promotion Gap · **NOT** Ground Truth Gap.

---

## Scope (authorized)

1. **Corpus-list retrieval boost** — secondary merge for OR-3-class queries
2. **Bibliography-Master §A.1/A.2/A.3 priority** in merged context
3. **Grounding instruction** — FONDAMENTALE / SUPPORTO / PERIFERICO taxonomy
4. Coherence audit on OR-3 canonical query
5. Validation script + unit tests

### Out of scope

- Ground Truth edits
- Corpus / thesis content edits
- New Decisions.md rows
- re-QWO C.3-R4 inside EWO-4A

---

## Deliverable chain

```text
EWO-4A implemented → QC PASS → audit PASS → C.3-R4
```

---

## Success criteria

1. Merged OR-3 retrieval includes Bibliography-Master chunks
2. Merged context includes Eco and Flügel markers
3. Grounding prompt includes A.1/A.2/A.3 taxonomy instruction on corpus queries
4. Unit tests green
5. EWO-4A report PASS
