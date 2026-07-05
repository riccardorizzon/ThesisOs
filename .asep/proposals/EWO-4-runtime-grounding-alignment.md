# Engineering WorkOrder Proposal — EWO-4

> **Status:** ✅ **APPROVED + IMPLEMENTED** (2026-06-30) — report `.asep/reports/EWO-4-runtime-grounding-alignment.md`  
> **Spawned from:** `.asep/reports/C.3-R2-investigation.md` (investigation ACCEPTED)  
> **EWO category:** **Grounding** (new — cognitive context pipeline)  
> Program: `.asep/programs/thesis-agent-migration.yaml`

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | EWO-4 |
| **Type** | EWO |
| **EWO category** | **Grounding** — align runtime prompt construction with binding decisions |
| **Capability** | `ewo-4-runtime-grounding-alignment` |
| **Lifecycle** | `approved` → `implemented` (on success) |
| **Blocks** | re-QWO C.3-R3 until implemented |

---

## Objective

Align the runtime **Grounding** layer with binding M2 decisions and Ground Truth
hierarchy — without promoting new documents.

Fix: Ground Truth → **Retrieval** → **Grounding** → Reasoning pipeline gap exposed by C.3-R2.

---

## Evidence (investigation ACCEPTED)

| Finding | Class |
|---------|-------|
| M2 `decisions` not in chat prompt path | Grounding Gap |
| `prompt_wire` instructs model to deny answers not in `[n]` sources | Grounding Gap |
| OR-3 query top-10 lacks exclusion chunks | Ranking Gap |
| C.3-R1 vs C.3-R2 variance | Model Variance |

**NOT** Structural / Promotion Gap.

---

## Scope (authorized)

1. **Prompt pipeline** — binding decisions in system prefix; hierarchy vs retrieval
2. **M2 decisions priority** — load `decisions` key into prompt context
3. **Grounding instruction** — apply frozen decisions even when sources omit them
4. **Exclusion-aware retrieval** — secondary merge for corpus/exclusion queries
5. **Coherence audit** — prompt contains CORPUS; exclusion chunks retrievable
6. Report + idempotent validation script

### Out of scope

- Ground Truth edits
- Thesis content edits
- New Decisions.md rows
- re-QWO C.3-R3 inside EWO-4
- Document promotion (Alignment)

---

## Cognitive pipeline (framework)

```text
Ground Truth → Retrieval → Grounding → Reasoning → Response
```

This EWO mutates **Grounding** (+ minor **Retrieval** augmentation).

---

## Success criteria

1. M2 `decisions` rendered in chat system prefix (`[BINDING DECISIONS]`)
2. Grounding prompt respects binding decisions over contradictory sources
3. Corpus/exclusion queries merge exclusion-relevant chunks
4. Unit tests green
5. Coherence audit PASS in EWO-4 report

---

## WO-TRACE

```text
C.3-R2 FAIL → INVESTIGATE (ACCEPTED) → EWO-4 Grounding → C.3-R3
```
