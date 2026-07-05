# Qualification WorkOrder Proposal — C.1

> **Status:** ✅ **Accepted** (2026-06-30) — user decision `C.1-R2: ACCEPTED`  
> **Qualification runs:** `C.1-R1` FAIL → EWO-1 → `C.1-R2` **PASS** · `or-1` **qualified**
>
> Per Engineering Program: `.asep/programs/thesis-agent-migration.yaml`
> Spec base: `knowledge/thesis-agent/_migration/operational-readiness.md` § OR-1
> **Metodo QWO:** this proposal supersedes hardcoded chapter counts in OR-1 evaluation.

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | C.1 |
| **Type** | **QWO** (Qualification WorkOrder) — validation only, no system mutation |
| **Capability** | `or-1-thesis-structure` |
| **Lifecycle** | `specified` → **`approved`** (2026-06-30) → `qualified` (on PASS) |
| **Program** | `thesis-agent-migration` · run `kimi-claw-2026-06` |
| **Approval** | `C.1 proposal: approved` + Structure Resolution Rule |

---

## Objective

Dimostrare che il **runtime ThesisOS vivo** ricostruisce autonomamente la
**struttura canonica della tesi attualmente approvata** — domanda generale, unità
strutturali (capitoli/sezioni/appendici come definiti nell'outline congelato),
obiettivo di ciascuna unità, sequenza logica, distinzioni esplicite nell'outline
(es. teoria vs caso studio) — utilizzando **esclusivamente** conoscenze già promosse
in memoria, documenti indicizzati e capitoli M6.

Non verifica che i file markdown in `knowledge/thesis-agent/` esistano (già provato
in baseline). Verifica che l'**agente operativo** sappia rispondere.

---

## Structure Resolution Rule

OR-1 verifica la capacità del runtime di ricostruire la **struttura canonica della
tesi attualmente approvata**.

La verifica **non dipende dal numero dei capitoli**, ma dalla capacità di recuperare
fedelmente la struttura definita come **Ground Truth** — l'outline congelato approvato,
oggi materializzato in repo come `03_PROJECT/Outline-Master.md` (unità strutturali,
titoli, obiettivi, ordine, distinzioni esplicite).

| Ruolo | Definizione |
|-------|-------------|
| **Ground Truth (valutazione)** | Outline congelato approvato — contenuto dinamico, non hardcoded |
| **Sorgenti agente (runtime)** | Solo knowledge **promossa** (M2 memories, M3/M4 documents, M6 chapters) |
| **PASS** | Output agente fedele al Ground Truth, ricostruito solo da sorgenti runtime |
| **FAIL qualificazione** | Qualsiasi differenza materiale tra output e Ground Truth, **oppure** impossibilità di ricostruire il Ground Truth dalle sole sorgenti promosse |

Un FAIL per gap di promozione (Ground Truth non presente nel runtime) **non** è un
errore del protocollo OR-1. È l'esito corretto del QWO → evidenza → **EWO separato**
→ re-QWO.

Il protocollo OR-1 resta valido se l'outline evolve (5, 6, 3A, appendici): cambia
solo il contenuto del Ground Truth, non la forma del test.

## Scope

### In scope (execution phase — after approval)

- Una sessione di prova sullo stack live (`make up`, `/chat` o API equivalente)
- Prompt di test OR-1 (testo canonico sotto)
- Raccolta output integrale dell'agente
- Valutazione PASS / PARTIAL / FAIL vs criteri e **oracle** (sotto)
- Aggiornamento `operational-readiness-log.md` + report `.asep/reports/C.1-or-1.md`

### Out of scope (explicit)

- Nessuna modifica a `knowledge/thesis-agent/**`
- Nessuna modifica a `memories` / `documents` / `chapters` via API
- Nessuna modifica a `backend/` / `frontend/`
- Nessun commit di codice o documentazione salvo log e report di prova
- Nessun OR-2 … OR-7, E2E, release

---

## Preconditions

| Precondition | Expected state | Verification (pre-flight, post-approval) |
|--------------|----------------|------------------------------------------|
| META-0 frozen | `meta-0-program-binding` lifecycle=frozen | `.asep/capabilities/thesis-agent-migration.yaml` |
| Phase A done | UNI-01, REL-01 | `Decisions.md` |
| Phase B done | memories + docs + chapters promoted | `promotion-log.md`; `curl /memory`, `/documents`, `/chapters` |
| Engineering Program active | program yaml + graph | `.asep/programs/thesis-agent-migration.yaml` |
| Live stack | backend `/health` → 200 | `curl http://localhost:8000/health` |
| Proposal approved | this document status → approved | **User explicit approval** |

---

## Test protocol

### Canonical prompt (OR-1)

```text
Spiega la struttura completa della tesi: domanda generale, capitoli, obiettivo di
ciascun capitolo e sequenza logica. Non inventare sezioni fuori outline.
```

### Runtime boundary (hard)

L'agente sotto prova **non deve** accedere a:

- File workspace `knowledge/thesis-agent/` (evaluator may; agent may not)
- Export `_inbox/kimi-claw/`
- Web / fonti esterne
- Contesto conversazionale non derivato dal turno corrente

**Allowed runtime surfaces:** prompt injection via M2 (`editable`, `thesis`, `decision`),
M3/M4 retrieval over promoted documents, M6 chapter metadata/content if routed.

**Operator constraint:** invocare solo `/chat` (o API chat) con sessione pulita;
non allegare file; non incollare outline da clipboard.

### Evaluation oracle (evaluator only)

**Ground Truth:** `03_PROJECT/Outline-Master.md` (+ coerenza con `Decisions.md` per
distinzioni esplicite, es. STIGMATA caso applicativo).

Confronto output agente vs Ground Truth. L'evaluator **può** leggere repo; l'agente **no**.

| Oracle aux | Path | Use |
|------------|------|-----|
| Thesis description | `03_PROJECT/Thesis-Description.md` | Allineamento domanda / intent |
| Promoted surfaces | `/memory`, `/documents`, `/chapters` | Inventario sorgenti runtime al momento del test |
| Promotion audit | diff Ground Truth vs contenuto promosso | Classificare causa FAIL (agent vs gap) |

### Known promotion gap (pre-flight note)

Al momento dell'approvazione, `Outline-Master.md` **non è promosso** in runtime (Fase B).
Ground Truth esiste in repo ma non interamente nelle sorgenti promosse → **FAIL atteso**
se non si promuove prima outline. Comportamento corretto del processo:

```text
QWO → FAIL → Evidence → EWO (promozione outline) → QWO → PASS
```

Un QWO **non corregge mai** il sistema (vedi `docs/engineering-program.md` § QWO discipline).

## Success criteria (PASS)

Applicazione della **Structure Resolution Rule**:

1. **Domanda generale** coerente con Ground Truth (Outline-Master)
2. **Tutte le unità strutturali** presenti nel Ground Truth (capitoli, sezioni,
   appendici — qualunque sia il loro numero o naming) con titolo e **funzione/obiettivo**
   corretti
3. **Sequenza logica** esplicita e allineata al Ground Truth
4. **Distinzioni esplicite** nel Ground Truth (es. teoria vs caso STIGMATA) presenti
   nell'output se definite nell'outline
5. **Nessuna unità strutturale inventata** non presente nel Ground Truth
6. Ricostruzione ottenuta **senza** violare runtime boundary — output tracciabile alle
   sorgenti promosse (memories + retrieval + chapters), non a file repo letti dall'agente
7. Output **autosufficiente** per il valutatore

Esito: **PASS** in `operational-readiness-log.md` colonna OR-1 → lifecycle `qualified`.

---

## Failure criteria (FAIL)

- Unità strutturali mancanti rispetto al Ground Truth
- Ordine o gerarchia errati
- Obiettivi/funzioni di unità strutturali materially wrong
- Distinzioni esplicite nel Ground Truth assenti o invertite
- Unità strutturali inventate (non nel Ground Truth)
- Informazioni contraddittorie vs `Decisions.md` congelate
- **Impossibilità** di ricostruire il Ground Truth dalle sole sorgenti promosse
  (classificare: *promotion gap* → aprire EWO, non patch in QWO)
- Violazione runtime boundary (evaluator rileva input da repo durante sessione agente)

Qualsiasi differenza materiale runtime-output vs Ground Truth = **FAIL di qualificazione**.

---

## Partial criteria (PARTIAL)

- Copertura corretta su un sottoinsieme delle unità strutturali del Ground Truth, con
  lacune documentate e causa identificata (agent limitation vs promotion gap)
- Domanda generale corretta ma obiettivi di unità incomplete
- Richiede accettazione esplicita utente prima di proseguire OR-2 o di spawnare EWO

PARTIAL **non** avanza lifecycle a `qualified` senza decisione utente.

## Evidence (deliverables post-execution)

| Artifact | Content |
|----------|---------|
| `knowledge/thesis-agent/_migration/operational-readiness-log.md` | Nuova riga per run (`C.1-R1`, `C.1-R2`, …) con OR-1 = PASS \| PARTIAL \| FAIL |
| `.asep/reports/C.{n}-R{k}.md` | Prompt, output integrale, checklist criteri, verdict motivato, oracle diff |
| (optional) transcript | ID sessione / timestamp / route usata (`conversation` vs `grounded_chat`) |

**Run naming:** ogni riesecuzione è una nuova istanza (`C.1-R1`, `C.1-R2`, …). I report
precedenti restano immutati. Vedi `docs/engineering-program.md`.

---

## Impact analysis

| Area | Impact |
|------|--------|
| Architecture | **None** — QWO |
| Runtime code | **None** |
| Knowledge / memory | **None** |
| Capability lifecycle | `or-1` → `qualified` if PASS; unchanged if FAIL |
| Program roadmap | Unblocks `or-2` only on PASS (or accepted PARTIAL) |
| Risk surfaced | Possibile gap promozione `Outline-Master` → future **EWO**, not part of C.1 |

---

## Rollback

Non applicabile. QWO di sola validazione; unico artefatto mutabile = log + report
(reversibili via git).

---

## Approval gate

**Approved 2026-06-30** with Structure Resolution Rule.

Execution authorized for operator dispatch (pre-flight → protocol → report).
QWO discipline: **no system mutation** during execution.

Post-execution:

1. Report + log
2. Lifecycle `or-1-thesis-structure`: `approved` → `qualified` (if PASS)
3. If FAIL (promotion gap): spawn **EWO proposal** — do not fix inside C.1

## Relationship to WorkOrder types

| Type | Mutates system | Example |
|------|----------------|---------|
| **EWO** Engineering WorkOrder | Yes (code, docs, memory, promotion) | META-0, Fase B, future outline ingest |
| **QWO** Qualification WorkOrder | No (evidence + log only) | **C.1 OR-1**, C.2–C.7, D.1 E2E |

See `docs/engineering-program.md` § WorkOrder types.

---

## Recommended next action

1. Operator: pre-flight preconditions → execute QWO C.1 protocol
2. If FAIL + promotion gap documented → Engineering Proposal for EWO (outline → runtime)
3. If PASS → unblock `or-2-stigmata-framework` (C.2 proposal before run)
