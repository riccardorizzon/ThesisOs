# Operational Readiness — gate finale migrazione

Run: `kimi-claw-2026-06`. **Ultimo gate** prima di dichiarare la migrazione conclusa.

> Non basta che i file esistano. ThesisOS deve **lavorare** come Kimi Claw:
> ricostruire, spiegare, decidere, scrivere e aggiornare senza re-imparare.

**Due livelli di verifica operativa:**

| Livello | Cosa verifica |
|---------|---------------|
| **OR-1 … OR-7** | Capacità singole (unit test) |
| **E2E** | Flusso continuo di sessione reale (integration test) |

**ThesisOS operativo** ⇔ OR tutti PASS **e** E2E PASS.

**Prerequisiti** ✅ (2026-06-30):

1. ~~Revisione e approvazione `University-Rules.md`~~ → UNI-01
2. ~~Validazione pattern relatrice R1–R5 → `Relatrice-Rules.md`~~ → REL-01
3. ~~Promozione regole in runtime + ingest corpus + capitoli (M6)~~ → Fase B

**Governance:** eseguire OR/E2E come WorkOrders del programma
`.asep/programs/thesis-agent-migration.yaml` (vedi `docs/engineering-program.md`).

**Solo dopo** i prerequisiti si esegue questo gate sul **agente ThesisOS vivo**
(chat/API con memoria e RAG attivi), non solo sui file markdown.

---

## Come si valuta

| Esito | Significato |
|-------|-------------|
| **PASS** | Risposta corretta, completa, coerente con artefatti congelati; nessuna invenzione; regole rispettate |
| **PARTIAL** | Sostanza corretta ma lacune, o dipendenza da file non promossi in runtime |
| **FAIL** | Informazione errata, regola violata, decisione già chiusa riaperta, attribuzione fantasma |

**Migrazione conclusa** ⇔ tutti e 7 i test **PASS** (zero FAIL; PARTIAL ammessi solo
se documentati e accettati esplicitamente da te).

Registrare ogni esecuzione in `_migration/operational-readiness-log.md` (data, esito,
note).

---

## OR-1 — Ricostruire la struttura completa della tesi

> **Metodo QWO (C.1):** valutazione governata da **Structure Resolution Rule** in
> `.asep/proposals/C.1-or-1-thesis-structure.md` — sostituisce riferimenti hardcoded
> al numero di capitoli. Ground Truth = outline congelato approvato (`Outline-Master.md`).

**Prompt di test:**

> Spiega la struttura completa della tesi: domanda generale, capitoli, obiettivo di
> ciascun capitolo e sequenza logica. Non inventare sezioni fuori outline.

**Criteri PASS (via Structure Resolution Rule):**

- Output fedele al **Ground Truth** (outline congelato — unità strutturali dinamiche)
- Domanda generale, titoli, obiettivi/funzioni, sequenza, distinzioni esplicite nell'outline
- Ricostruito solo da knowledge **promossa** in runtime
- Nessuna unità strutturale inventata

**Fonti agente (runtime):** memories + documents + chapters promossi.
**Oracle valutatore:** `Outline-Master.md`, `Thesis-Description.md`, `Decisions.md`.

**Baseline markdown-only (2026-06-30):** ✅ PASS su repo — non sostituisce QWO C.1 live.

---

## OR-2 — Framework STIGMATA e uso nella tesi

**Prompt di test:**

> Cos'è STIGMATA nella tesi? Qual è il framework documentale? Come si collega ai capitoli
> teorici senza diventare oggetto principale di ricerca?

**Criteri PASS:**

- STIGMATA = caso applicativo / verifica metodologica, non oggetto teorico principale
- Cita `Stigmata-Framework.md`: DOCUMENTATION_MASTER, evidence-first, livelli evidenza
- Spiega che il cap. 5 legge STIGMATA **attraverso** categorie dei cap. 1–4
- Non tratta STIGMATA come autobiografia o marketing

**Fonti attese:** `Stigmata-Framework.md`, `Decisions.md` METH-02, `Outline-Master.md`

**Baseline attuale:** ✅ PASS su markdown — framework materializzato; evidenza binaria assente (noto).

---

## OR-3 — Corpus: elenco e quando usare ciascuna fonte

**Prompt di test:**

> Elenca gli autori del corpus attivo. Per ciascuno: opera, capitolo/i tesi, ruolo
> (fondamentale/supporto). Indica cosa è escluso e perché.

**Criteri PASS:**

- ~12 autori attivi da `Bibliography-Master.md` / `Core-Theory-Map.md`
- Barthes *Mythologies* e Bourriaud **esclusi** con riferimento a `Decisions.md`
- Per ogni autore fondamentale: indica **quando** citarlo (es. Löbach → cap. 1 struttura;
  Albers → cap. 3 colore; Warburg → cap. 2 moodboard se nel map)
- Non propone nuove fonti senza classificarle candidate

**Fonti attese:** `Bibliography-Master.md`, `Core-Theory-Map.md`, `Decisions.md`

**Baseline attuale:** ✅ PASS su markdown.

---

## OR-4 — Regole università e relatrice applicabili

**Prompt di test:**

> Elenca tutte le regole università e della relatrice attualmente applicabili alla
> stesura. Distingui obblighi istituzionali da preferenze di progetto.

**Criteri PASS:**

- Regole università da `University-Rules.md` **approvato** (non bozza)
- Regole relatrice da `Relatrice-Rules.md` **solo voci validate** (stato = validata)
- Distingue: guida Accademia vs preferenza progetto (es. note minimizzate)
- Cita REV-001–006 dove pertinenti
- **Non** inventa regole da trascrizioni non validate

**Fonti attese:** `University-Rules.md`, `Relatrice-Rules.md`, `05_MEMORY/Permanent.md`

**Baseline attuale:** ✅ **PASS** su agente vivo (C.4-R1, 2026-06-30).

---

## OR-5 — Decisioni prese vs ancora aperte

**Prompt di test:**

> Quali decisioni sono già congelate? Quali sono ancora aperte? Cosa non si deve
> riproporre?

**Criteri PASS:**

- Elenca fasi congelate: CORPUS v2.1, BIBLIOGRAFIA v1.0, OUTLINE v1.0, META-DOCUMENTI
- Elenca esclusioni corpus (Barthes, Bourriaud) e REV-001–006
- Indica decisioni aperte da `Decisions.md` § "Da decidere" e `Thesis-State.md`
- **Non** suggerisce di rifare stress test corpus o riaprire bibliografia senza trigger

**Fonti attese:** `Decisions.md`, `Thesis-State.md`, `Changelog.md`

**Baseline attuale:** ✅ **PASS** su agente vivo (C.5-R1, 2026-06-30). Contratto: `.asep/proposals/C.5-or-5-decision-lifecycle.md`.

---

## OR-6 — Scrivere un nuovo paragrafo rispettando regole e stile

**Prompt di test:**

> Scrivi un paragrafo di prova per [es. §3.2 colore e Albers] in modalità scrittura
> accademica. Applica REV-006, separazione A/B, livelli FONDATO, firewall persona OFF.

**Criteri PASS:**

- Registro accademico neutro; **zero** emoji/esclamazioni (persona OFF)
- Separazione A (Albers) / B (applicazione tesi)
- Nessuna citazione diretta tradotta; attribuzioni verificabili
- Etichetta stato: bozza / PRONTO PER REVISIONE (non congela unilateralmente)
- Rispetta regole relatrice validate (R1–R5) se applicabili
- Non cita autori esclusi dal corpus

**Fonti attese:** runtime memories + `Writing-Rules.md` + `Relatrice-Rules.md` + outline

**Baseline attuale:** ✅ **PASS\*** — C.6-R3 live (2026-07-01); W-06 = Platform Limitation documentata.

---

## OR-7 — Memory Runtime Integrity (session closure)

**Capability class:** Memory Runtime Integrity · **Sensitivity:** Deterministic

**Prompt di test (scenario simulato — canonical C.7):**

> Abbiamo appena completato una bozza per §3.2 colore (Albers). Chiudi la sessione di lavoro:
> proponi MEMORY UPDATE, fonte candidata, aggiornamento Thesis-State §3.2, riga Changelog,
> coerenza Bibliography. Non scrivere in permanente senza approvazione. Non modificare congelati.

Vedi proposta completa: `.asep/proposals/C.7-or-7-memory-runtime-integrity.md` (oracle M-01…M-09).

**Criteri PASS (sintesi):**

- Formato `Memory-Protocol.md` (MEMORY UPDATE PROPOSAL) — **non** scrive in permanente senza approvazione
- Nuova fonte → candidata in `Bibliography.md`, non attiva senza decisione
- Aggiornamento stato → proposta per `Thesis-State.md` + riga `Changelog.md`
- Nessuna modifica artefatti Frozen
- Ogni modifica riferibile a fonte identificabile
- **State Atomicity (M-09):** bundle coerente — nessun artefatto aggiornato senza i sibling

**Fonti attese:** `Memory-Protocol.md`, `Bibliography.md`, `Thesis-State.md`, `Changelog.md`, `Decisions.md`

**Baseline attuale:** ✅ **PASS** — C.7-R1 live (2026-07-01); M-01…M-09; traceability 100%.

---

## Riepilogo baseline (2026-06-30, post-QWO live)

| Test | Esito markdown | Esito agente vivo | Ultimo run |
|------|----------------|-------------------|------------|
| OR-1 Struttura tesi | ✅ PASS | ✅ **PASS** | C.1-R2 |
| OR-2 STIGMATA | ✅ PASS | ✅ **PASS** | C.2-R2 |
| OR-3 Corpus | ✅ PASS | ✅ **PASS** | C.3-R4 |
| OR-4 Regole uni + relatrice | ✅ PASS | ✅ **PASS** | C.4-R1 |
| OR-5 Decisioni | ✅ PASS | ✅ **PASS** | C.5-R1 |
| OR-6 Scrittura paragrafo | ✅ PASS* | ✅ **PASS\*** | C.6-R3 (W-06 platform limitation) |
| OR-7 Memory Runtime Integrity | ✅ PASS | ✅ **PASS** | C.7-R1 |
| E2E Integrazione | — | ✅ **PASS** | e2e-2026-07-01 |

**Verdetto:** OR-1…OR-7 **PASS/PASS\*** · **E2E PASS** · **E.1 COMPLETE** — **ThesisOS v1.0 Operational**.

Log autoritativo: `_migration/operational-readiness-log.md`.

---

## E2E — End-to-End Project Test (gate integrazione)

> **OR-1 … OR-7** = test di **capacità singole** (unità).
> **E2E** = test di **flusso continuo** (integrazione): simula una vera sessione di lavoro
> sulla tesi senza perdere contesto.

**Obiettivo:** certificare che ThesisOS è pronto a diventare l'**ambiente di lavoro
definitivo**, non solo a rispondere a prompt isolati.

**Prerequisiti:** identici a OR (Fase A + B completate) **e** tutti OR-1 … OR-7 = PASS.

**Esecuzione:** una **singola sessione continua** (stesso thread/contesto agente). Vietato
"reimpostare" il contesto tra uno step e l'altro. Tu osservi e approvi dove richiesto
(MEMORY UPDATE, fonte candidata → attiva).

### No Hidden Operator Intervention (binding — D.1 2026-07-01)

During E2E, **no operator action** may alter system state between steps:

- no manual edits to `Thesis-State`, memory, or corpus files;
- no runtime restart;
- no prompt or oracle modification mid-session;
- no manual state injection into DB.

E2E must be a **continuous session** — the test validates real usage conditions.
Operator chat approvals (`sì/no`) within the same thread are allowed (G5); silent
filesystem/DB mutations between steps are not.

### Scenario consigliato (default run `e2e-2026-06`)

| Parametro | Valore |
|-----------|--------|
| Fonte | `04_KNOWLEDGE/Books/Albers_Interaction-of-Color.md` (corpus attivo) |
| Obiettivo outline | §3.2 colore / interazione cromatica (`Outline-Master.md`) |
| Paragrafo output | Bozza per sezione outline non ancora congelata (es. §3.2) |
| Nota | Resta nel corpus congelato; **non** introduce autori nuovi |

Variante accettabile (con tua approvazione esplicita): fonte **candidata** non nel corpus
per verificare che resti candidata e non entri in scrittura.

### Sequenza E2E (6 step — flusso continuo)

#### E2E-1 — Leggere una fonte del corpus

**Azione agente:** library-first su Albers (identificazione, estrazione A/B, citation bank
ridotto) per il paragrafo target.

**PASS se:**

- Legge da `04_KNOWLEDGE/Books/` o retrieval M4 (non inventa contenuto)
- Separa A (autore) / B (tesi)
- Etichetta FONDATO / PLAUSIBILE / SPECULATIVO
- Non riapre fasi congelate (CORPUS, BIBLIOGRAFIA, OUTLINE)

**FAIL se:** attribuzione fantasma, mix A/B, propone espandere corpus senza classificare
candidata.

---

#### E2E-2 — Aggiornare la bibliografia

**Azione agente:** aggiorna riferimento/pagina/citazione chiave per Albers se emersa
dall'audit; altrimenti documenta "nessun aggiornamento necessario" con motivazione.

**PASS se:**

- Modifica coerente con `Bibliography-Master.md` / `Bibliography.md`
- Non contraddice edizioni congelate
- Se aggiunge voce: classificazione corretta (attiva / candidata / scartata)

**FAIL se:** altera BIBLIOGRAPHY_MASTER congelato senza trigger; aggiunge autore escluso.

---

#### E2E-3 — Aggiornare memoria (se necessario)

**Azione agente:** valuta se emerge regola/preferenza da memorizzare; se sì → **MEMORY UPDATE
PROPOSAL** (non scrive in permanente unilateralmente).

**PASS se:**

- Usa formato `Memory-Protocol.md`
- Attende approvazione prima di scrivere in `Permanent.md` / DB `memories`
- Se nulla da memorizzare: lo dichiara esplicitamente

**FAIL se:** scrive memoria permanente senza approvazione; memoria fantasma.

---

#### E2E-4 — Proporre integrazione nell'outline

**Azione agente:** indica **dove** nel `Outline-Master` la lettura di Albers rafforza o
precisa §3.2; non modifica outline congelato unilateralmente.

**PASS se:**

- Riferimento preciso a sezione outline esistente
- Propone integrazione come **nota di lavoro** o bozza, non riscrittura outline
- Rispetta REV-006 e perimetro capitolo 3

**FAIL se:** aggiunge sezioni non approvate; riapre OUTLINE_MASTER v1.0 congelato.

---

#### E2E-5 — Scrivere paragrafo (regole automatiche)

**Azione agente:** produce paragrafo accademico per §3.2 (o sezione concordata).

**PASS se (cumulativo):**

- **Università:** `University-Rules.md` approvato (citazioni, registro, note)
- **Relatrice:** `Relatrice-Rules.md` validate (R1–R5 se applicabili)
- **Progetto:** REV-006, A/B, FATTO/INFERENZA/VALUTAZIONE, firewall persona OFF
- Stato esplicito: **PRONTO PER REVISIONE** (non congelato)
- Nessun autore escluso (Barthes, Bourriaud)

**FAIL se:** viola una regola sopra; tono chat/contamina tesi; congela unilateralmente.

---

#### E2E-6 — Aggiornare stato progetto + changelog

**Azione agente:** aggiorna `Thesis-State.md` (es. §3.2 bozza pronta per revisione) +
riga in `05_MEMORY/Changelog.md` con data, file, azione, sintesi.

**PASS se:**

- Stato coerente con output E2E-5
- Changelog tracciabile (cosa, perché, quale fonte/step)
- In runtime: eventuali record M6 coerenti con mirror markdown

**FAIL se:** stato incoerente; nessun changelog; perde tracciabilità verso E2E-1…5.

---

### Criteri globali E2E (tutto il flusso)

Il test E2E è **PASS** solo se **tutti** E2E-1 … E2E-6 passano **e**:

| # | Criterio globale |
|---|------------------|
| G1 | **Contesto continuo** — nessun reset; riferimenti coerenti tra step |
| G2 | **Decisioni chiuse** — non ripropone stress test, ampliamento corpus, riformulazione THEORY MAP |
| G3 | **Tracciabilità** — ogni output risalibile a fonte + step precedente |
| G4 | **Regole** — zero violazioni università / relatrice / progetto |
| G5 | **Approvazioni** — MEMORY UPDATE e promozioni fonte solo con tuo OK |

**FAIL globale** se uno step fallisce o se G1–G5 violati.

---

### Registrazione E2E

In `operational-readiness-log.md`, sezione dedicata:

```text
E2E run: e2e-YYYY-MM-DD
Scenario: [fonte] → [sezione outline]
E2E-1 … E2E-6: PASS|FAIL + note
G1 … G5: PASS|FAIL
Verdetto E2E: PASS|FAIL
Osservatore: [utente]
```

---

### Gerarchia gate (baseline definitiva migrazione)

```
Post-migrazione audit (10 aree)     → integrità export
        ↓
OR-1 … OR-7 (capacità singole)      → agente vivo, tutti PASS
        ↓
E2E (sessione continua)             → flusso reale tesi, PASS
        ↓
ThesisOS OPERATIVO / migrazione CONCLUSA
```

**Migrazione conclusa** ⇔ OR tutti PASS **e** E2E PASS.

---

## Sequenza di chiusura definitiva

```
Fase A — Tu (in corso)
  [ ] Revisione University-Rules.md → "university-rules: ok"
  [ ] Validazione R1–R5 → Relatrice-Rules.md

Fase B — Promozione runtime
  [ ] memories (editable, thesis, decision)
  [ ] documents M3 + retrieval M4
  [ ] chapters M6

Fase C — Operational Readiness
  [x] OR-1 … OR-7 su agente vivo → PASS/PASS*
  [x] Registrare in operational-readiness-log.md

Fase D — End-to-End Project Test
  [x] E2E-1 … E2E-6 in sessione continua → PASS + G1–G5
  [x] Registrare in operational-readiness-log.md

Fase E — Release Baseline (E.1)
  [x] v1.0 Operational freeze → ThesisOS OPERATIVO / migrazione CONCLUSA
```

---

## Relazione con altri documenti

| Documento | Ruolo |
|-----------|-------|
| `post-migration-validation.md` | Audit post-migrazione (10 aree + stress test T1–T7) |
| `operational-readiness.md` | Gate operativo: **OR-1 … OR-7** + **E2E** — questo file |
| `operational-readiness-log.md` | Registro esecuzioni e esiti |
| `Relatrice/transcription/VALIDATION.md` | Supporto per R1–R5 (prerequisito OR-4) |
