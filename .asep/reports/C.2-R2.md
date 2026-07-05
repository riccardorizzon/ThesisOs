# QWO C.2-R2 — OR-2 Re-Qualification Report

**Date:** 2026-06-30  
**WorkOrder:** C.2 · **Type:** QWO · **Run:** **#2** (`C.2-R2`)  
**Capability:** `or-2-stigmata-framework`  
**Conversation id:** `3c1ba5a4-0080-4b60-b787-d8f806ad5bbd`  
**Message id:** `e73510c1-f119-45ac-bf1d-540c8a0c6a35`  
**Verdict:** **PASS**

**Precondition:** EWO-2 implemented (`.asep/reports/EWO-2-runtime-methodology-alignment.md`).  
**Prior run:** `C.2-R1` → PARTIAL (accepted) — preserved, not superseded.

---

## 1. Pre-flight

| Check | Result |
|-------|--------|
| `/health` | 200 OK |
| EWO-2 implemented | ✅ Stigmata-Framework indexed |
| `Stigmata-Framework.md` | id `e7540d4e-…` — **indexed**, 49 chunks |
| `Outline-Master.md` | indexed |
| `decisions` memory | METH-02/METH-04 present |
| Proposal C.2 + Qualification Contract | approved |
| New conversation | ✅ `3c1ba5a4-0080-4b60-b787-d8f806ad5bbd` |
| System mutations | **None** |

---

## 2. Test protocol

**Prompt (OR-2 canonical):**

```text
Cos'è STIGMATA nella tesi? Qual è il framework documentale? Come si collega ai capitoli
teorici senza diventare oggetto principale di ricerca?
```

**Runtime boundary:** single POST `/chat`, new session, no attachments.  
**Duration:** ~55s

---

## 3. Agent output (integral)

Certamente. In base ai documenti forniti, ecco una sintesi del ruolo di STIGMATA nella tesi, del suo framework documentale e del metodo per mantenerlo come caso studio.

### 1. Cos'è STIGMATA nella tesi?

STIGMATA non è l'oggetto principale della ricerca, ma il **caso studio applicativo** utilizzato per verificare la metodologia proposta dalla tesi [2]. [...]

### 2. Qual è il framework documentale?

Il framework documentale è un sistema rigoroso che collega ogni **materiale documentale** del progetto STIGMATA a un **concetto teorico** del corpus della tesi. [...]

| Materiale documentale | Concetto teorico collegato | Autore di riferimento | Stato dell'evidenza (se non verificato) |
| :--- | :--- | :--- | :--- |
| **Bozzetti e diari di lavorazione** | Processo creativo strutturato in fasi; iteratività. | **Löbach** | NON VERIFICABILE (critico) [5, 8] |
| **Moodboard e riferimenti visivi** | Ricerca come memoria delle immagini [...] | **Warburg, Benjamin, Seivewright** | NON VERIFICABILE (critico) [4, 5, 8] |
| **Foto dei capi finiti** | Analisi del prodotto come segno, forma, colore. | (Autori del cap. 3) | NON VERIFICABILE (critico) [5] |
| **Foto di fitting e note tecniche** | Pratica manuale come pensiero [...] | **Sennett** | NON VERIFICABILE (alto rischio) [5] |
| **Appunti e diari riflessivi** | Esperienza soggettiva del processo (es. *flow*); pratica riflessiva. | **Csikszentmihalyi** | NON VERIFICABILE (medio rischio) [5, 8] |

Il framework distingue tra ciò che è **FONDATO** (provato da documenti), **PLAUSIBILE** (logico ma non provato) e **APPLICAZIONE TESI** (un'interpretazione originale della tesi, non attribuibile a un autore) [8].

### 3. Come si collega ai capitoli teorici senza diventare oggetto principale?

[...] Subordinazione dell'analisi alla teoria [...] Gestione rigorosa dei "vuoti teorici" [...] Struttura argomentativa cap. 1-4 / 5 / 6 [...]

*(4371 characters — full text captured in execution log.)*

---

## 4. Ground Truth vs output (Qualification Contract)

| Contract element | Result |
|------------------|--------|
| **METH-02** — caso applicativo, non oggetto principale | ✅ |
| **DOCUMENTATION_MASTER** — tassonomia materiale (bozzetti, moodboard, fitting, …) | ✅ Tabella categorie + link teoria |
| **METH-04** — evidence-first | ✅ Promozione plausibile→fondato via prove |
| **Livelli evidenza** FONDATO / PLAUSIBILE / NON VERIFICABILE / APPLICAZIONE TESI | ✅ Nominati con senso GT |
| **Cap. 5** — categorie cap. 1–4 (Löbach, Warburg, Sennett, cap. 3, flow) | ✅ |
| **Non autobiografia / marketing** | ✅ Meccanismi espliciti |
| **Materiale assente** — NON VERIFICABILE, non inventato | ✅ Coerente con framework vuoto |
| **Runtime boundary** | ✅ |

**Material differences:** none triggering FAIL or PARTIAL.

**Improvement vs C.2-R1:** DOCUMENTATION_MASTER taxonomy + evidence levels now present; framework da Stigmata-Framework promosso, non solo outline §5.

---

## 5. Checklist (Qualification Contract)

| Criterion | Result |
|-----------|--------|
| METH-02 ruolo STIGMATA | ✅ |
| DOCUMENTATION_MASTER (categorie principali) | ✅ |
| Evidence-first METH-04 | ✅ |
| Livelli evidenza nominati | ✅ |
| Cap. 5 ↔ categorie teoretiche | ✅ |
| No autobiografia / marketing | ✅ |
| No materiale fantasma popolato | ✅ |
| Runtime boundary | ✅ |
| Output autosufficiente | ✅ |

**Overall: PASS**

---

## 6. Lifecycle & next steps

| Field | Value |
|-------|-------|
| `or-2-stigmata-framework` lifecycle | **`qualified`** |
| OR-2 log (C.2-R2) | **PASS** |
| Unblocks OR-3 | **Yes** — C.3 proposal before run |

**Historical record:** C.2-R1 PARTIAL remains valid evidence of pre-EWO-2 state.

**State transition (Engineering State Machine):**

```text
WorkOrder: C.2-R2 (QWO)
Verdict: PASS
Report: C.2-R2.md
Lifecycle: approved → qualified
```

---

## 7. Artifacts updated (QWO-allowed)

- `knowledge/thesis-agent/_migration/operational-readiness-log.md`
- This report
- Capability graph lifecycle update

**No** changes to knowledge, memory, documents, runtime code.

---

```text
QWO C.2-R2 Status: PASS
or-2-stigmata-framework → qualified
Recommended Next: C.3 proposal → OR-3 QWO
```
