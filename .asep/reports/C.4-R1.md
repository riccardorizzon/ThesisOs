# QWO C.4-R1 — OR-4 Constraint Compliance Report

**Date:** 2026-06-30  
**WorkOrder:** C.4 · **Type:** QWO · **Run:** **#1** (`C.4-R1`)  
**Capability:** `or-4-rules` · **Domain:** Normative · **Sensitivity:** deterministic  
**Conversation id:** `6e7489ac-58bf-4617-ab99-6c6f57cbbc0e`  
**Message id:** `92e42a7a-0dfe-4720-b964-d429e2ad6474`  
**QC Certificate:** `.asep/certificates/C.4-R1-20260630.yaml`  
**Verdict:** **PASS**

**Precondition:** C.4 approved · pre-flight measured Runtime Coverage **90%**  
**Prior runs:** none

---

## 1. Pre-flight

| Check | Result |
|-------|--------|
| `/health` | 200 OK |
| Pre-flight audit | ✅ `.asep/reports/C.4-preflight-runtime-audit.md` |
| Measured Runtime Coverage | **90%** (authorizes QWO) |
| QC Certificate | PASS |
| New conversation | ✅ |
| System mutations | **None** |

---

## 2. Test protocol

**Prompt (OR-4 canonical):**

```text
Elenca tutte le regole università e della relatrice attualmente applicabili alla
stesura. Distingui obblighi istituzionali da preferenze di progetto.
```

**Duration:** ~58.5s · **Sources (SSE):** 10 · **Output length:** 5485 chars

---

## 3. Agent output (summary)

- **Hierarchy** explicit: institutional → relatrice → project decisions ✅
- **Institutional (UNI-01):** structure §3.1 order, 80.000 battute triennale, A4/margins/interlinea/font sizes, citation integrity, virgolette caporali, infratesto, bibliografia alfabetica, immagini numerate ✅
- **Supervisor (REL-01):** R1–R5 all listed with correct substance ✅
- **Footnote ban:** stated as **vietate** with UNI-01 / RED-02; conflict table vs guida that allows notes ✅
- **Autore-date:** mandatory in project layer ✅
- **Distinction table:** institutional option vs project/restrictive choice ✅
- **REV-006** cited in interpretation row ✅
- **Residual:** table cites **REL-03** for footnote alignment — **wrong ID** (REL-03 is not a relatrice rule; R3 / RED-02 apply). Substance correct; label error only.

---

## 4. Oracle diff (N-01…N-12)

| ID | Element | Result |
|----|---------|--------|
| N-01 | 80.000 battute triennale | ✅ |
| N-02 | Struttura ordine §3.1 | ✅ |
| N-03 | Autore-date nel corpo | ✅ |
| N-04 | Nessuna nota a piè di pagina | ✅ **vietate** |
| N-05 | R1 nome completo + cognome | ✅ |
| N-06 | R2 attribuzione | ✅ |
| N-07 | R3 un concetto / citazioni corpo | ✅ |
| N-08 | R4 prudenza | ✅ |
| N-09 | R5 lessico | ✅ |
| N-10 | REV-001–006 where pertinent | ⚠️ REV-006 only (acceptable vs contract) |
| N-11 | Distinction institutional / relatrice / project | ✅ |
| N-12 | No invented unvalidated rules | ⚠️ REL-03 mis-label (not unvalidated transcription) |

---

## 5. Sub-capability matrix

| Sub-cap | Verdict | Signal |
|---------|---------|--------|
| **C.4.1 Acquisition** | **PASS** | ≥90% oracle elements; traceable to M2 UNI/REL/decisions |
| **C.4.2 Interpretation** | **PASS** | N-11 satisfied; 1 ID mis-label (REL-03) ≤ threshold |
| **C.4.3 Enforcement** | **PASS** | Footnote ban + autore-date without softening |
| **C.4.4 Conflict Resolution** | **PASS** | Table: guida allows notes → project **vietate**; UNI layer preserved |

**Composite aggregation (§9):** all sub-cap PASS → parent PASS.

---

## 6. Normative FAIL test cases

| ID | Result | Notes |
|----|--------|-------|
| NF-01 Footnote prohibition | ✅ PASS | Vietate + autore-date |
| NF-02 Citation style | ✅ PASS | Autore-date obbligatorio |
| NF-03 Layer confusion | ✅ PASS | RED-02 / project vs institutional separated |
| NF-04 Institutional omission | ✅ PASS | Footnote ban in table |
| NF-05 Invented supervisor rule | ⚠️ minor | REL-03 label wrong; R3 substance OK |
| NF-06 Unvalidated transcription | ✅ PASS | — |
| NF-07 Precedence error | ✅ PASS | Project restriction does not override UNI base |
| NF-08 Scientific bleed | ✅ PASS | CORPUS-01 labeled as project decision |
| NF-09 Structural ghost | ✅ PASS | Rules traceable to promoted sources |
| NF-10 Softening obligation | ✅ PASS | «Vietate», not «discouraged» |

**Material NF failures:** **0**

---

## 7. Capability Coverage

```text
Ground Truth Coverage:     100%
Runtime Coverage:          90% (measured pre-flight; re-confirmed)
Qualification Coverage:    PASS (100%)
Evidence Coverage:         100%
Traceability Coverage:     ~88% (estimate)
```

**Traceability worksheet:**

| Metric | Score |
|--------|-------|
| Anchored claims ([n], UNI/REL/RED) | ~90% |
| Layer labels correct | ~85% (REL-03 slip) |
| Oracle N-01…N-12 in output | 11/12 full · 1 partial (REV set) |
| **Weighted Traceability** | **~88%** (≥80% PASS threshold) |

---

## 8. WO-TRACE

```text
C.4 approved → pre-flight 90% → C.4-R1 PASS
```

---

## 9. Lifecycle

| Field | Value |
|-------|-------|
| `or-4-rules` lifecycle | **`qualified`** |
| OR-4 log | **PASS** (C.4-R1) |
| Unblocks | **C.5** proposal (OR-5) |

---

## 10. Residual (non-blocking)

- **REL-03 mis-citation** in comparison table — should reference **R3** / **RED-02** / **UNI-01 §8**. Record for future Attribution-style tightening under Normative domain; does not reopen C.4.3 Enforcement.

**No EWO-5A / EWO-5B required.**
