# QWO C.3-R4 — OR-3 Re-Qualification Report

**Date:** 2026-06-30  
**WorkOrder:** C.3 · **Type:** QWO · **Run:** **#4** (`C.3-R4`)  
**Capability:** `or-3-corpus` · **Sensitivity:** retrieval-sensitive  
**Conversation id:** `818d5c0e-8a61-4c26-a32c-5b98084a4791`  
**Message id:** `147c32e8-b49d-4782-aeab-200af59cddda`  
**Verdict:** **PASS**

**Precondition:** EWO-4 + **EWO-4A** implemented; backend rebuilt  
**Prior runs:** C.3-R1 PARTIAL (accepted) · C.3-R2 FAIL · C.3-R3 PARTIAL (rejected)

---

## 1. Pre-flight

| Check | Result |
|-------|--------|
| `/health` | 200 OK |
| EWO-4 + EWO-4A | ✅ live in container |
| EWO-4A audit | ✅ PASS |
| New conversation | ✅ |
| System mutations | **None** |

---

## 2. Test protocol

**Prompt (OR-3 canonical):** unchanged.

**Duration:** ~62s · **Sources:** 12

---

## 3. Agent output (summary)

- **12/12 autori** con ruolo A.1/A.2/A.3 corretto
- **Fondamentali (4):** Löbach, Csikszentmihalyi, Sennett, Warburg — opere + capitoli ✅
- **Supporto (7):** Benjamin, Albers, Hollander, Barthes (*Sistema moda*), Dorfles, **Eco**, Seivewright ✅
- **Periferico (1):** **Flügel** ✅
- **Esclusioni:** Mythologies (CORPUS-02) + Bourriaud (CORPUS-03) ✅
- **Capitoli:** mapping da Outline-Master ✅
- **Opere supporto:** alcune «Non specificata» — accettabile vs contract (ruolo + autore completi)

---

## 4. Ground Truth vs output

| Contract element | C.3-R3 | C.3-R4 | Result |
|------------------|--------|--------|--------|
| ~12 autori + ruolo | 10/12 | **12/12** | ✅ |
| Fondamentali (4) | mis-label | **4/4 correct** | ✅ |
| Eco / Flügel | missing | **present** | ✅ |
| CORPUS-02/03 | ✅ | ✅ | ✅ |
| Barthes = *Sistema moda* | ✅ | ✅ | ✅ |
| FOND / SUPPORTO / PERIFERICO | confused | **aligned §A.1–A.3** | ✅ |
| Capitoli mapping | partial | **substantially complete** | ✅ |

---

## 5. WO-TRACE

```text
C.3-R2 FAIL → EWO-4 (exclusions)
  → C.3-R3 PARTIAL → REJECTED
  → EWO-4A (corpus-list retrieval)
  → C.3-R4 PASS
```

---

## 6. Capability Coverage

```text
Ground Truth Coverage:     100%
Runtime Coverage:          ~100%
Qualification Coverage:    PASS (100%)
Evidence Coverage:         100%
```

---

## 7. Lifecycle

| Field | Value |
|-------|-------|
| `or-3-corpus` lifecycle | **`qualified`** |
| OR-3 log | **PASS** (C.3-R4) |
| Unblocks | **C.4** proposal (META-1 gate) |

---

## 9. Traceability Coverage (indicative)

Assessed per `docs/asep-capability-model.md`:

| Signal | Assessment |
|--------|------------|
| Claims with `[n]` or CORPUS anchor | High (~90%+) |
| 12/12 entities → GT section | ✅ |
| Support-author opera titles | Partial — lowers **C.3.4 Attribution** |

**Traceability Coverage (estimate):** ~85% — does not invalidate PASS; documents residual Attribution sub-cap gap.

---

## 8. Remediation attribution

| Run | Primary gap | Fix |
|-----|-------------|-----|
| C.3-R2 | Grounding (exclusions) | EWO-4 |
| C.3-R3 | Retrieval + Reasoning (completeness) | EWO-4A |
| C.3-R4 | — | PASS |
