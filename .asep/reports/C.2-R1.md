# QWO C.2-R1 — OR-2 Qualification Report

**Date:** 2026-06-30  
**WorkOrder:** C.2 · **Type:** QWO · **Run:** **#1** (`C.2-R1`)  
**Capability:** `or-2-stigmata-framework`  
**Conversation id:** `e4b0c047-0851-494a-a9c2-d67eabf8332f`  
**Message id:** `fbce645c-f50e-41c1-8104-83e3ecc11ce6`  
**Verdict:** **PARTIAL**

**Proposal:** `.asep/proposals/C.2-or-2-stigmata-framework.md` (approved 2026-06-30)  
**Precondition:** `or-1` qualified (C.1-R2 PASS accepted). **No system mutations** during QWO.

---

## 1. Pre-flight

| Check | Result |
|-------|--------|
| `/health` | 200 OK |
| Proposal approved | ✅ Qualification Contract binding |
| `thesis` memory | v4 (EWO-1 aligned) |
| `decisions` memory | `decisions`, `university-rules`, `relatrice-rules` |
| `Outline-Master.md` | ✅ indexed, 43 chunks |
| **`Stigmata-Framework.md`** | ❌ **not in runtime** (M3/M4) |
| New conversation | ✅ `e4b0c047-0851-494a-a9c2-d67eabf8332f` |
| System mutations | **None** |

**Promoted surfaces relevant to OR-2:**

| Surface | STIGMATA / framework coverage |
|---------|------------------------------|
| M2 `thesis` | Cap. 5 role, METH-02 ref, artefatto path (not body) |
| M2 `decisions` | METH-02, METH-04 (summary) |
| M2 `editable` | evidence-first, STIGMATA subordinate |
| M3/M4 `Outline-Master` | Cap. 5 §5.1–5.3 objectives, material types in paragraph specs |
| M3/M4 `Stigmata-Framework` | **Absent** — DOCUMENTATION_MASTER, EVIDENCE MATRIX, evidence levels |

---

## 2. Test protocol

**Prompt (OR-2 canonical):**

```text
Cos'è STIGMATA nella tesi? Qual è il framework documentale? Come si collega ai capitoli
teorici senza diventare oggetto principale di ricerca?
```

**Runtime boundary:** single POST `/chat`, new session, no attachments, no operator paste.  
**Route observed:** `null`; citations `[1]…[6]` → retrieval from promoted docs (primarily Outline cap. 5).

**Duration:** ~54s

---

## 3. Agent output (integral)

Sulla base dei documenti forniti, ecco una spiegazione dettagliata del ruolo di STIGMATA nella tesi, del suo framework documentale e del suo rapporto con i capitoli teorici.

### 1. Cos'è STIGMATA nella tesi?

STIGMATA è il **caso studio applicativo** della tesi, non il suo oggetto di ricerca principale. Il suo ruolo è quello di fungere da terreno di verifica per la metodologia e le categorie teoriche elaborate nei capitoli precedenti [2].

In sintesi, STIGMATA è:
*   Una collezione o progetto di fashion design intitolato "STIGMATA: lettura analitica di un processo", a cui è dedicato il capitolo 5 [2].
*   Un **esempio pratico** utilizzato per dimostrare come il processo creativo nel fashion design possa essere documentato, analizzato e letto come una "costruzione di senso" attraverso la pratica riflessiva [1, 6].
*   Lo strumento che permette alla tesi di passare dalla teoria alla pratica, mostrando l'applicabilità delle teorie di autori come Löbach, Warburg e Benjamin a un processo creativo concreto [3, 4].

Il suo ruolo è definito in modo esplicito e vincolante: "**STIGMATA non è l'oggetto della tesi, ma il caso studio che ne verifica la metodologia**" [2].

### 2. Qual è il framework documentale?

Il "framework documentale" non è un singolo documento, ma l'**approccio metodologico** con cui il caso STIGMATA viene analizzato nel capitolo 5, utilizzando i materiali d'archivio del progetto come prove documentali. Questo framework si articola in tre passaggi principali:

1.  **Analisi del processo produttivo secondo Löbach**: [...] **bozzetti, moodboard, foto di processo e diari di lavorazione** [3].
2.  **Analisi della ricerca visiva secondo Warburg e Benjamin**: [...] moodboard [...] Warburg [...] Benjamin [...] [4].
3.  **Sintesi della lettura analitica**: [...] documentazione di un processo articolato [...] [6].

### 3. Come si collega ai capitoli teorici senza diventare l'oggetto principale?

[...] **Funzione di verifica** [...] **Disciplina probatoria** [...] **Separazione tra descrizione e interpretazione** [...] **Obiettivo finale metodologico** [...] pratica riflessiva [1, 5].

*(4645 characters — full text captured in execution log.)*

---

## 4. Ground Truth vs output (Qualification Contract)

**Ground Truth:** `Stigmata-Framework.md` + `Decisions.md` (METH-02, METH-04) + `Outline-Master.md` § Cap. 5

| Contract element | GT requirement | Output | Result |
|------------------|----------------|--------|--------|
| **METH-02** | Caso applicativo, non oggetto principale | Esplicito, citazione verbatim outline | ✅ |
| **Cap. 5** | Applica categorie cap. 1–4 | Löbach, Warburg, Benjamin; verifica metodologica | ✅ (parziale: cap. 3–4 categorie non esplicitate come layer) |
| **Evidence-first** | METH-04, prove documentali | «Disciplina probatoria», bozzetti/foto/diari | ✅ |
| **DOCUMENTATION_MASTER** | Tassonomia infrastruttura v1.0 (BZ, MB, CP, WP, FT, FF, TC, AD, …) | Non nominato; 4 tipi materiali da outline §5, non master tabellare | ❌ |
| **EVIDENCE MATRIX** | Collegamento materiale ↔ concetti | Assente | ❌ |
| **Livelli evidenza** | FONDATO / PLAUSIBILE / NON VERIFICABILE (+ APPLICAZIONE TESI) | Non menzionati | ❌ |
| **Stato materiale vuoto** | Framework dichiara NON VERIFICABILE / tabelle vuote | Non esplicitato | ⚠️ |
| **Non autobiografia** | Outline §5.2 | Separazione descrizione/interpretazione enfatizzata | ✅ |
| **Non marketing** | — | Nessuna deriva promozionale | ✅ |
| **Materiale inventato** | — | Nessuna affermazione che archivio sia popolato | ✅ |

---

## 5. Failure classification

| Cause | Assessment |
|-------|------------|
| **Promotion gap** | **Primary.** `Stigmata-Framework.md` not promoted; agent cannot retrieve DOCUMENTATION_MASTER, EVIDENCE MATRIX, evidence-level taxonomy |
| **Partial recovery** | Outline cap. 5 + thesis/decisions → correct role + cap. 5 analytic structure + evidence-first prose |
| **Agent error** | **Secondary.** Framework reframed as «approccio metodologico» a 3 passaggi (outline narrative) vs infrastruttura documentale congelata |
| **QWO protocol** | ✅ No corrective mutations |

**Valid PARTIAL** per Qualification Contract. Non autorizza patch nel QWO.

---

## 6. Checklist (Qualification Contract)

| Criterion | Result |
|-----------|--------|
| METH-02 ruolo STIGMATA | ✅ |
| DOCUMENTATION_MASTER (categorie principali) | ❌ |
| Evidence-first METH-04 | ✅ |
| Livelli evidenza nominati | ❌ |
| Cap. 5 ↔ categorie teoretiche | ✅ (parziale) |
| No autobiografia / marketing | ✅ |
| No materiale fantasma | ✅ |
| Runtime boundary | ✅ |
| Output autosufficiente | ✅ |
| Ricostruzione GT completa da sole sorgenti promosse | ❌ (gap) |

**Overall: PARTIAL** — sufficient for role/link; **insufficient for PASS** (framework documentale GT incomplete).

---

## 7. Lifecycle & next steps

| Field | Value |
|-------|-------|
| `or-2-stigmata-framework` lifecycle | **`specified` → `approved`** (unchanged — **not** `qualified`) |
| OR-2 log (C.2-R1) | **PARTIAL** |
| Unblocks OR-3 | **No** |

**Outer Loop decision (2026-06-30):** `C.2-R1: ACCEPTED` — PARTIAL valid; conceptual model coherent with promoted knowledge; document gap → **EWO-2 spawned**.

**Recommended path (authorized):**

```text
C.2-R1 PARTIAL (accepted)
        → EWO-2 Runtime Methodology Alignment
        → re-QWO C.2-R2
```

---

## 8. Artifacts updated (QWO-allowed)

- `knowledge/thesis-agent/_migration/operational-readiness-log.md`
- This report

**No** changes to knowledge, memory, documents, runtime code.

---

```text
QWO C.2-R1 Status: PARTIAL (accepted)
Primary cause: promotion gap — Stigmata-Framework.md not in runtime
Next: EWO-2 proposal spawned → execution approval → C.2-R2
```
