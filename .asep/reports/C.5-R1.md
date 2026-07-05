# QWO C.5-R1 — OR-5 Decision Lifecycle Integrity Report

**Date:** 2026-06-30  
**WorkOrder:** C.5 · **Type:** QWO · **Run:** **#1** (`C.5-R1`)  
**Capability:** `or-5-decisions` · **Domain:** Organizational · **Sensitivity:** deterministic  
**Conversation id:** `ed9226af-793c-4fef-9186-433c12ae01e9`  
**Message id:** `eef982c1-c0d0-48a5-b8b2-989f2644e066`  
**QC Certificate:** `.asep/certificates/C.5-R1-20260630.yaml`  
**Verdict:** **PASS**

**Precondition:** C.5 approved with refinement · pre-flight **80%** measured  
**Prior runs:** none

---

## 1. Pre-flight

| Check | Result |
|-------|--------|
| `/health` | 200 OK |
| Pre-flight audit | ✅ `.asep/reports/C.5-preflight-runtime-audit.md` |
| Measured Runtime Coverage | **80%** |
| QC Certificate | PASS |
| New conversation | ✅ |
| System mutations | **None** |

---

## 2. Test protocol

**Prompt (OR-5 canonical):**

```text
Quali decisioni di progetto sono congelate e quali restano aperte? Per ciascuna indica
lo stato nel ciclo di vita (congelata / aperta). Cosa non si deve riproporre senza
trigger esplicito?
```

**Duration:** ~63.5s · **Sources (SSE):** 10 · **Output length:** 4988 chars

---

## 3. Agent output (summary)

- **Lifecycle labels:** explicit **Congelata** / **Aperta** sections ✅
- **Frozen phases / masters:** CORE THEORY MAP v2.1, BIBLIOGRAPHY_MASTER v1.0, OUTLINE_MASTER v1.0, STIGMATA framework v1.0 ✅
- **Decision IDs:** CORPUS-01…04, METH-01…04, REV-001–006, RED-01…03, UNI-01 §8, RED-02 ✅
- **Open (§ Da decidere):** checklist §13, M6 auto-persist policy, reimport cap. 1–2 ✅
- **Decision Consistency:** non-reproposal lists exclusions, footnotes ban, outline freeze, methodology — no corpus stress-test redo or bibliography reopen ✅
- **Residual:** adds STIGMATA material recovery as «critica/aperta» (framework context, not in Decisions.md § Da decidere); Benjamin/fascism tangent in non-reproposal §5 (noise)

---

## 4. Oracle diff (D-01…D-12)

| ID | Element | Result |
|----|---------|--------|
| D-01 | Fase CORPUS congelata | ✅ via CORPUS-01 + Core-Theory-Map v2.1 |
| D-02 | BIBLIOGRAFIA v1.0 | ✅ |
| D-03 | OUTLINE v1.0 | ✅ |
| D-04 | META-DOCUMENTI / STIGMATA framework | ✅ |
| D-05 | CORPUS-02/03 esclusi | ✅ |
| D-06 | REV-001–006 | ✅ |
| D-07 | METH-02 (+ METH-01/03/04) | ✅ |
| D-08 | § Da decidere (≥3 items) | ✅ all three |
| D-09 | Decision Consistency | ✅ no lifecycle-incompatible reopen |
| D-10 | Decision object vs fact | ✅ IDs + lifecycle states |
| D-11 | No OR-3 primary bleed | ✅ decision-centric answer |
| D-12 | No invented binding IDs | ⚠️ STIGMATA materials as open — contextual, no fake ID |

---

## 5. Sub-capability matrix

| Sub-cap | Verdict | Signal |
|---------|---------|--------|
| **C.5.1 Decision Acquisition** | **PASS** | ≥85% oracle elements; CORPUS/REV/METH/RED/UNI traceable |
| **C.5.2 Lifecycle State Recognition** | **PASS** | Congelata/Aperta consistent |
| **C.5.3 Closure Integrity** | **PASS** | Frozen set + GT open backlog complete |
| **C.5.4 Decision Consistency** | **PASS** | No Frozen-as-Draft recommendations |

**Composite aggregation (§9):** all sub-cap PASS → parent PASS.

---

## 6. Organizational FAIL test cases

| ID | Result | Notes |
|----|--------|-------|
| OF-01 | ✅ | No corpus stress-test redo |
| OF-02 | ✅ | No bibliography reopen |
| OF-03 | ✅ | CORPUS-02/03 frozen/excluded |
| OF-04 | ✅ | Open items present |
| OF-05 | ✅ | Decision framing |
| OF-06 | ✅ | Not OR-3 author-list answer |
| OF-07 | ✅ | No invented decision IDs |
| OF-08 | ✅ | No unfreeze language on frozen phases |
| OF-09 | ✅ | Traceable to M2 decisions/thesis |
| OF-10 | — | n/a |

**Material OF failures:** **0**

---

## 7. Artifact Issues (parallel taxonomy — non-blocking)

| Issue | Class | Notes |
|-------|-------|-------|
| STIGMATA materials as 4th «open decision» | Contextual expansion | Valid framework concern; not in Decisions.md § Da decidere — record only |
| Benjamin/fascism in non-reproposal §5 | **Formatting / relevance noise** | Not a capability FAIL |

---

## 8. Capability Coverage

```text
Ground Truth Coverage:     100%
Runtime Coverage:          80% (measured pre-flight)
Qualification Coverage:    PASS (100%)
Evidence Coverage:         100%
Traceability Coverage:     ~86% (estimate)
```

---

## 9. WO-TRACE

```text
C.5 approved (refinement) → pre-flight 80% → C.5-R1 PASS
```

---

## 10. Lifecycle

| Field | Value |
|-------|-------|
| `or-5-decisions` lifecycle | **`qualified`** |
| OR-5 log | **PASS** (C.5-R1) |
| Unblocks | **C.6** proposal (OR-6) |

**No EWO-6A / EWO-6B required.**
