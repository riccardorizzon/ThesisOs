# QWO C.3-R1 — OR-3 Corpus Qualification Report

**Date:** 2026-06-30  
**WorkOrder:** C.3 · **Type:** QWO · **Run:** **#1** (`C.3-R1`)  
**Capability:** `or-3-corpus`  
**Conversation id:** `478cbcd5-0817-46f5-977c-07e085257ac9`  
**Message id:** `dcfc98f3-e743-4781-8a4a-e712a81947ee`  
**Verdict:** **PARTIAL**

**Precondition:** Pre-flight audit complete — Runtime Coverage **40%**  
(`.asep/reports/C.3-preflight-runtime-audit.md`).  
**Authorization:** Operator `C.3-R1: approved` — no runtime/knowledge/memory mutations.

---

## 1. Pre-flight

| Check | Result |
|-------|--------|
| `/health` | 200 OK |
| `or-2` qualified | ✅ C.2-R2 PASS |
| EWO-1, EWO-2 | ✅ implemented |
| Proposal C.3 + Qualification Contract | ✅ approved |
| Pre-flight Runtime Coverage | **40%** (masters absent; books 8/8) |
| New conversation | ✅ `478cbcd5-0817-46f5-977c-07e085257ac9` |
| System mutations | **None** |
| Repository access during test | **None** (agent under test) |

### Capability Coverage (snapshot)

```text
Ground Truth Coverage:     100%
Runtime Coverage:          40%
Qualification Coverage:    PARTIAL (~45% — see §6)
Evidence Coverage:         100%
```

---

## 2. Test protocol

**Prompt (OR-3 canonical):**

```text
Elenca gli autori del corpus attivo. Per ciascuno: opera, capitolo/i tesi, ruolo
(fondamentale/supporto). Indica cosa è escluso e perché.
```

**Runtime boundary:** single POST `/chat`, new session, no attachments.  
**Duration:** ~59s

---

## 3. Agent output (integral)

Certamente. Ecco un'analisi del corpus autori basata sui documenti forniti e sulle regole di progetto memorizzate.

### Corpus Attivo

Di seguito gli autori confermati come parte del corpus attivo del progetto, con il loro ruolo e i capitoli di pertinenza.

| Autore | Opera di Riferimento | Ruolo e Capitoli Tesi |
| :--- | :--- | :--- |
| **Richard Sennett** | *L'uomo artigiano* (2008) [8] | **Fondamentale.** Il suo concetto di "making is thinking" (fare è pensare) è centrale per legittimare la pratica manuale come fase di elaborazione concettuale. È l'autore principale per il **Capitolo 4: La pratica manuale: fare come pensare** [8]. |
| **Walter Benjamin** | *L'opera d'arte nell'epoca della sua riproducibilità tecnica* [3, 4, 6, 9, 10] | **Fondamentale.** Utilizzato per analizzare il cambiamento di statuto dell'oggetto di design e della sua percezione. I suoi concetti (perdita dell'aura, ricezione distratta, critica alla "creatività" tradizionale) sono trasversali e applicabili principalmente al **Capitolo 2** (sulla raccolta e trasformazione dei riferimenti) e al **Capitolo 3** (sulla lettura del prodotto) [6, 9, 10]. |
| **Josef Albers** | L'opera non è specificata nelle fonti, ma la sua presenza è confermata [8]. | **Supporto/Fondamentale (per sezione specifica).** È richiamato nel contesto della progettazione e dell'analisi del rapporto tra progetto e materia [8]. Il suo ruolo è probabilmente centrale per le sezioni del **Capitolo 3** dedicate al colore e alla forma. |
| **Anne Hollander, Gillo Dorfles** | Le opere specifiche non sono menzionate, ma la loro presenza nel corpus è confermata [5]. | **Supporto.** Sono citati come parte del quadro teorico, ma le fonti indicano che non coprono concetti specifici del caso STIGMATA come "corpo come soglia" o "topologia del capo" [5]. Il loro contributo è probabilmente legato all'analisi della forma, del segno e del valore culturale del capo nel **Capitolo 3**. |

---

### Autori e Concetti Esclusi o da Gestire con Cautela

| Autore / Concetto | Stato | Motivazione |
| :--- | :--- | :--- |
| **Roland Barthes (*Mythologies*)** | **Escluso.** | Come da regole di progetto, l'opera *Mythologies* è stata esplicitamente esclusa per non deviare dal perimetro della ricerca. Tuttavia, l'autore Barthes potrebbe essere presente con altre opere (es. *Il sistema della moda*) per l'analisi semiotica nel Capitolo 3, come suggerito dalla fonte [5]. L'esclusione è quindi specifica per *Mythologies*. |
| **Nicolas Bourriaud** | **Escluso.** | Le fonti fornite non lo menzionano, ma le regole di progetto indicano che il suo filone di pensiero (es. *Estetica Relazionale*) è stato scartato dal corpus per mantenere la tesi focalizzata sul processo creativo individuale e materico. |
| **Concetti senza copertura teorica** | **Da trattare come applicazione.** | Concetti come "corpo come soglia", "topologia" e "linea come confine", pur essendo presenti nel caso studio STIGMATA, non sono coperti da autori del corpus [5]. Il protocollo richiede di presentarli come letture proposte dalla tesi e non come teorie fondate su autori approvati [5]. |

In sintesi, il corpus è costruito per supportare l'analisi del processo creativo in tutte le sue fasi, dalla ricerca [Benjamin] alla progettazione [Albers] fino alla realizzazione pratica [Sennett], con un apparato critico per leggere il prodotto finale [Dorfles, Hollander, Barthes]. Le esclusioni servono a mantenere il focus del lavoro, mentre le regole per i "vuoti teorici" garantiscono il rigore metodologico nell'analisi del caso studio [5].

*(3569 characters)*

---

## 4. Ground Truth vs output (Qualification Contract)

**Ground Truth:** `Bibliography-Master.md` v1.0 + `Core-Theory-Map.md` v2.1 + `Decisions.md` CORPUS-01…04

### Author oracle (12 autori attivi, CORPUS-01)

| # | Autore | GT ruolo | GT capiti | In output | Match |
|---|--------|----------|-----------|-----------|-------|
| 1 | Löbach | FONDAMENTALE | Cap. 1 | ❌ assente | ❌ |
| 2 | Csikszentmihalyi | FONDAMENTALE | Cap. 1 | ❌ assente | ❌ |
| 3 | Sennett | FONDAMENTALE | Cap. 3, 4 | ✅ Cap. 4 citato | ⚠️ cap. 3 omesso |
| 4 | Warburg | FONDAMENTALE | Cap. 2 | ❌ assente | ❌ |
| 5 | Albers | SUPPORTO | Cap. 3 | ✅ (opera non nominata) | ⚠️ |
| 6 | Hollander | SUPPORTO | Cap. 3 | ✅ (raggruppato) | ⚠️ opera assente |
| 7 | Barthes | SUPPORTO | Cap. 3 (*Sistema della moda*) | ⚠️ solo in esclusioni/sintesi | ⚠️ |
| 8 | Dorfles | SUPPORTO | Cap. 3 | ✅ (raggruppato) | ⚠️ opera assente |
| 9 | Eco | SUPPORTO | Cap. 3 | ❌ assente | ❌ |
| 10 | Benjamin | SUPPORTO | Cap. 2, 4 | ✅ | ❌ ruolo **Fondamentale** (GT: SUPPORTO) |
| 11 | Seivewright | SUPPORTO | Cap. 2 | ❌ assente | ❌ |
| 12 | Flügel | PERIFERICO | Cap. 5 | ❌ assente | ❌ |

**Authors present:** 6 / 12 (50%) · **Fondamentali present:** 1 / 4 (Sennett only; Löbach, Csikszentmihalyi, Warburg missing)

### Contract elements

| Contract element | GT requirement | Output | Result |
|------------------|----------------|--------|--------|
| ~12 autori attivi con opera e ruolo | Bibliography-Master A.1–A.3 | 6 autori, opere spesso vaghe | ❌ |
| Capitoli / quando citare (fondamentali) | Theory Map + Master | Solo Sennett cap. 4 esplicito | ❌ |
| CORPUS-02 — *Mythologies* escluso | Decisions | Escluso con motivazione | ✅ |
| CORPUS-03 — Bourriaud escluso | Decisions | Escluso con motivazione | ✅ |
| Barthes attivo = *Sistema della moda* | Master A.2.4 | Menzionato in nota esclusione | ⚠️ |
| FONDAMENTALE vs SUPPORTO | Master livelli | Benjamin errato; ruoli misti | ❌ |
| Nessuna fonte nuova non classificata | CORPUS-01 | Nessuna espansione proposta | ✅ |
| CORPUS-04 library-first | Decisions | Non citato (non richiesto esplicitamente nel prompt) | — |
| Ricostruzione GT da sole sorgenti promosse | Contract §PASS | Impossibile elenco completo | ❌ |

### Availability vs Applicability (framework principle)

| Signal | Availability | Applicability | Assessment |
|--------|--------------|---------------|------------|
| `Barthes_Mythologies.md` in runtime | ✅ retrievable | ✅ escluso da corpus attivo (CORPUS-02) | **Applicability PASS** |
| `Lobach_Disegno-Industriale.md` promoted | ✅ indexed | ❌ non elencato come autore attivo | Availability unused |
| `Bibliography-Master.md` | ❌ not promoted | ❌ master map unavailable | **Promotion gap** |
| `Core-Theory-Map.md` | ❌ not promoted | ❌ chapter/role map unavailable | **Promotion gap** |

Retrieving *Mythologies* is not an error; treating it as corpus attivo would be. Agent correctly applied CORPUS-02 despite OCR availability.

---

## 5. Failure classification

| Cause | Assessment |
|-------|------------|
| **Promotion gap** | **Primary.** `Bibliography-Master.md` + `Core-Theory-Map.md` not in runtime — agent cannot reconstruct full 12-author map, roles, chapter routing |
| **Partial recovery** | Books OCR + M2 decisions → 6 authors, exclusions CORRECT, STIGMATA vuoti teorici protocol |
| **Agent limitation** | **Secondary.** Löbach + Csikszentmihalyi promoted in Books but omitted from active corpus list; Benjamin role inverted |
| **Applicability** | **PASS** on CORPUS-02/03 despite contradictory Mythologies OCR in index |
| **QWO protocol** | ✅ No corrective mutations |

**Valid PARTIAL** per Qualification Contract §PARTIAL — not sufficient for PASS.

---

## 6. Checklist (Qualification Contract)

| Criterion | Result |
|-----------|--------|
| ~12 autori con opera e ruolo | ❌ (6/12) |
| Capitoli / quando citare | ❌ |
| Mythologies escluso (CORPUS-02) | ✅ |
| Bourriaud escluso (CORPUS-03) | ✅ |
| Barthes attivo ≠ Mythologies | ⚠️ |
| FONDAMENTALE vs SUPPORTO | ❌ |
| No espansione corpus non classificata | ✅ |
| Runtime boundary | ✅ |
| Output autosufficiente | ✅ |
| Ricostruzione GT completa da sole sorgenti promosse | ❌ |

**Overall: PARTIAL** — exclusions and applicability sound; **corpus map incomplete** (promotion gap + partial agent synthesis).

**Qualification Coverage estimate:** ~45% (6/12 authors + 2/2 exclusions + applicability bonus; role/chapter map failed).

---

## 7. Lifecycle & next steps

| Field | Value |
|-------|-------|
| `or-3-corpus` lifecycle | **`specified`** (unchanged — **not** `qualified`) |
| OR-3 log (C.3-R1) | **PARTIAL** |
| Unblocks OR-4 | **No** |

**Recommended path (WO-TRACE):**

```text
C.3-R1 PARTIAL
        → Outer Loop review
        → EWO-3 proposal (Alignment — promote Bibliography-Master + Core-Theory-Map)
        → re-QWO C.3-R2
```

**Candidate EWO-3 scope (proposal only — not executed in QWO):**

- Promote `Bibliography-Master.md` + `Core-Theory-Map.md` to M3/M4
- Verify M2 CORPUS-01…04 rows
- Optional: normalization note on `Barthes_Mythologies.md` vs CORPUS-02 (separate decision)

---

## 8. Artifacts updated (QWO-allowed)

| Artifact | Update |
|----------|--------|
| `.asep/reports/C.3-R1.md` | This report |
| `operational-readiness-log.md` | Row C.3-R1 |
| `.asep/capabilities/thesis-agent-migration.yaml` | `qualification_runs[]`, `coverage` |
| `.asep/reports/README.md` | Run index |
| `03_PROJECT/TODO.md` | C.3-R1 done |

**No mutations:** knowledge, memory, documents, runtime config.

---

## 9. WO-TRACE

```text
C.3 proposal approved
        → pre-flight (40% runtime)
        → C.3-R1 QWO → PARTIAL
        → (pending) Outer Loop → EWO-3 → C.3-R2
```

Prior run history preserved. Next run id: **`C.3-R2`**.
