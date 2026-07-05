# Qualification WorkOrder Proposal — C.2

> **Status:** ✅ **Approved** — C.2-R1 PARTIAL · C.2-R2 **PASS** · `or-2` **qualified**
>
> Program: `.asep/programs/thesis-agent-migration.yaml`  
> Spec base: `knowledge/thesis-agent/_migration/operational-readiness.md` § OR-2  
> Template: `.asep/templates/qualification-work-order-template.md` (Qualification Contract)

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | C.2 |
| **Type** | **QWO** (Qualification WorkOrder) — validation only |
| **Capability** | `or-2-stigmata-framework` |
| **Lifecycle transition** | `specified` → `approved` (on proposal approval) → `qualified` (on PASS) |
| **Program** | `thesis-agent-migration` · run `kimi-claw-2026-06` |
| **Depends on** | `or-1-thesis-structure` **qualified** (C.1-R2 PASS, accepted 2026-06-30) |
| **First run id** | `C.2-R1` (on approval) |

---

## Objective

Dimostrare che il **runtime ThesisOS vivo** spiega correttamente il **ruolo di STIGMATA**
nella tesi, il **framework documentale** congelato e il **collegamento metodologico** ai
capitoli teorici (1–4) — senza trattare STIGMATA come oggetto principale di ricerca né
come narrazione autobiografica/marketing — usando **esclusivamente** knowledge promossa.

Non verifica l'esistenza del materiale binario STIGMATA (assente per design). Verifica che
l'agente conosca l'**infrastruttura documentale** e le **regole probatorie** congelate.

---

## Qualification Contract

Contratto vincolante per l'esecuzione e la valutazione di questo QWO. L'evaluator giudica
**solo** rispetto a questo contratto; l'agente sotto test **non** accede al repo.

### Capability

`or-2-stigmata-framework` — OR-2 STIGMATA framework and role in thesis.

### Prerequisiti

| Precondition | Expected state | Verification |
|--------------|----------------|--------------|
| `or-1` qualified | lifecycle `qualified`, C.1-R2 PASS accepted | capability graph |
| EWO-1 implemented | outline + thesis memory aligned | `.asep/reports/EWO-1-runtime-knowledge-alignment.md` |
| Phase A / B | UNI-01, REL-01; memories + docs + chapters | `Decisions.md`, `promotion-log.md` |
| Live stack | `/health` → 200 | pre-flight |
| Proposal approved | this document → approved | **User explicit approval** |

### Ground Truth

Fonti autoritative per la valutazione (evaluator only):

| Priority | Artifact | Role |
|----------|----------|------|
| **Primary** | `03_PROJECT/Stigmata-Framework.md` v1.0 | DOCUMENTATION_MASTER, EVIDENCE MATRIX, livelli evidenza, workflow evidence-first |
| **Binding** | `03_PROJECT/Decisions.md` | METH-02 (caso applicativo), METH-04 (evidence-first), REV-006 |
| **Structural** | `03_PROJECT/Outline-Master.md` § Cap. 5 | Ruolo cap. 5, lettura analitica (non autobiografica), applicazione categorie cap. 1–4 |
| **Auxiliary** | `03_PROJECT/Project-Rules.md`, `05_MEMORY/Permanent.md` | Sintesi ruolo STIGMATA / evidence-first (non sostituiscono framework integrale) |

**Elementi GT obbligatori per PASS:**

1. **METH-02:** STIGMATA = caso applicativo / verifica metodologica, **non** oggetto teorico principale.
2. **Cap. 5:** legge STIGMATA **attraverso** categorie teoretiche cap. 1–4 (processo, ricerca, prodotto, pratica manuale).
3. **Framework documentale:** almeno **DOCUMENTATION_MASTER** (tassonomia materiale: bozzetti, moodboard, campionature, WIP, fitting, capi finali, testi, …) e principio **evidence-first** (METH-04).
4. **Livelli evidenza:** **FONDATO**, **PLAUSIBILE**, **NON VERIFICABILE** (+ distinzione dato documentale vs collegamento teorico / APPLICAZIONE TESI).
5. **Non deriva:** niente autobiografia, marketing, «significato personale» come centro; cap. 5 ≠ racconto di come è nata la collezione (Outline §5.2).

**Nota materiale binario:** assenza evidenza STIGMATA in export è **nota**, non FAIL di per sé — il framework dichiara tabelle vuote / NON VERIFICABILE.

### Runtime Boundary

**Agent under test must NOT use:**

- File workspace `knowledge/thesis-agent/` (evaluator may)
- Export `_inbox/kimi-claw/`
- Web / external sources
- Operator paste of framework from clipboard
- File attachments on `/chat`

**Allowed runtime surfaces (only):**

| Surface | Expected contribution |
|---------|----------------------|
| M2 `thesis` | Cap. 5 role, artefatto STIGMATA_FRAMEWORK in tabella master, stato stesura |
| M2 `decisions` | METH-02, METH-04, REV-006 |
| M2 `editable` | Project rules, evidence-first, confini STIGMATA |
| M3/M4 documents | **If promoted:** Stigmata-Framework, Outline-Master, Project-Rules, … |
| M6 chapters | Cap. 1–3 content (contesto teorico; no sostituto del framework) |

**Hard operator constraint:** single POST `/chat`, **new** `conversation_id`, canonical prompt only.

### Evidence Required

Post-execution artifacts (QWO-allowed mutations only):

| Artifact | Content |
|----------|---------|
| `.asep/reports/C.2-R1.md` | Pre-flight inventory, prompt, output integrale, oracle diff, checklist, verdict |
| `operational-readiness-log.md` | New row: run `C.2-R1`, OR-2 column |
| Transcript metadata | `conversation_id`, timestamp, route (if emitted), message_id |

Prior runs (`C.2-R2`, …) get **new report files**; history never overwritten.

### PASS Criteria

Output fedele al Ground Truth, ricostruibile dalle sorgenti promosse:

1. Definisce STIGMATA come **caso studio / verifica metodologica**, non oggetto teorico principale (METH-02).
2. Cita o ricostruisce **DOCUMENTATION_MASTER** (almeno le categorie principali del framework v1.0).
3. Spiega **evidence-first** per la narrativa processo STIGMATA (METH-04).
4. Nomina i **livelli evidenza** (FONDATO / PLAUSIBILE / NON VERIFICABILE) con senso corretto.
5. Spiega che il **cap. 5** applica categorie cap. 1–4 al caso STIGMATA (Outline §5).
6. **Non** centra STIGMATA come autobiografia, diario personale o comunicazione promozionale.
7. **Non** inventa materiale documentale esistente (framework attualmente vuoto / NON VERIFICABILE).
8. Output autosufficiente; nessuna violazione runtime boundary.

→ `or-2-stigmata-framework` lifecycle → **`qualified`**; OR-3 unblocked (C.3 proposal next).

### PARTIAL Criteria

- Ruolo METH-02 e collegamento cap. 5 corretti, ma **framework documentale incompleto** (es. manca DOCUMENTATION_MASTER o livelli evidenza).
- Evidence-first corretto ma EVIDENCE MATRIX assente.
- Causa classificata: **agent limitation** vs **promotion gap** (GT non interamente promosso).
- **Non** avanza lifecycle a `qualified` senza decisione utente esplicita.
- Outer Loop: accettare PARTIAL, spawnare EWO, o abortire.

### FAIL Criteria

- STIGMATA trattato come oggetto principale di ricerca o centro teorico.
- Cap. 5 descritto come racconto autobiografico / marketing / intento personale dominante.
- Categorie cap. 1–4 non collegate al caso studio.
- Framework inventato non presente in GT, o materiale documentale fantasma.
- Contraddizione materiale vs METH-02 / Outline §5.2 / Stigmata-Framework.
- **Impossibilità** di ricostruire GT dalle sole sorgenti promosse → classificare *promotion gap*.
- Violazione runtime boundary.

Qualsiasi differenza **materiale** output vs Ground Truth = FAIL di qualificazione.

### Spawn Rule (eventuale EWO)

```text
QWO C.2-Rk → FAIL or PARTIAL (promotion gap)
        → Evidence in C.2-Rk report
        → EWO proposal separata (es. EWO-2: promote Stigmata-Framework + sync memories)
        → NO patch durante QWO
        → re-QWO C.2-R{k+1}
```

**Known promotion gap (pre-approval audit 2026-06-30):**

| GT artifact | In runtime M3/M4? |
|-------------|-------------------|
| `Outline-Master.md` | ✅ indexed (EWO-1) |
| `Stigmata-Framework.md` | ❌ **not promoted** |
| METH-02 / METH-04 in M2 `decisions` | ✅ partial (Decisions memory) |
| Cap. 5 architecture in M2 `thesis` | ✅ partial |

Un FAIL per assenza di `Stigmata-Framework.md` nel runtime è **esito valido** del QWO — non autorizza
correzione in-sessione. Pattern identico a C.1-R1 → EWO-1.

**Candidate EWO (if gap confirmed):** promote `Stigmata-Framework.md` to M3/M4; optional PATCH
`thesis` / `decisions` con riferimento strutturale — **proposal EWO-2 separata**, non parte di C.2.

### Lifecycle Transition

| Verdict | Capability lifecycle | OR-2 log | Unblocks |
|---------|---------------------|----------|----------|
| **PASS** | `specified` → `approved` → **`qualified`** | PASS | `or-3-corpus` (C.3 proposal) |
| **PARTIAL** | unchanged (`approved`) | PARTIAL | nothing without user decision |
| **FAIL** | unchanged (`approved`) | FAIL | EWO proposal if structural gap |

Qualification run history appended to capability graph (`qualification_runs[]`); prior verdicts preserved.

---

## Scope

### In scope (after approval)

- Pre-flight: inventory promoted surfaces vs Ground Truth
- Execute **C.2-R1**: live `/chat`, new session, canonical prompt
- Evaluate vs Qualification Contract
- Report + operational log

### Out of scope

- Nessuna modifica a knowledge, memory, documents, chapters, backend, frontend
- Nessun OR-3 … OR-7, E2E, release
- Nessuna promozione `Stigmata-Framework` durante il QWO (→ EWO separato)
- Nessuna esecuzione finché questa proposal non è approvata

---

## Test protocol

### Canonical prompt (OR-2)

```text
Cos'è STIGMATA nella tesi? Qual è il framework documentale? Come si collega ai capitoli
teorici senza diventare oggetto principale di ricerca?
```

### Evaluation oracle (evaluator only)

Diff agent output vs Ground Truth (tabella sopra). Classificare gap:

| Class | Indicator |
|-------|-----------|
| **Promotion gap** | GT element missing from all promoted surfaces; agent partial answer from thesis/decisions only |
| **Agent error** | GT promoted but output wrong or collapsed |
| **Valid partial** | Role correct, framework detail missing — trace cause |

---

## Impact analysis

| Area | Impact |
|------|--------|
| Architecture | None |
| Runtime code | None |
| Knowledge / memory | None during QWO |
| Capability lifecycle | `or-2` → `qualified` on PASS only |
| Program | Unblocks OR-3 on PASS (or accepted PARTIAL) |
| Risk | Likely promotion gap on `Stigmata-Framework.md` → EWO-2 before re-QWO |

---

## Rollback

Non applicabile. Solo log + report mutabili (reversibili via git).

---

## Approval gate

**Not authorized until explicit approval**, e.g.:

```text
C.2 proposal: approved
```

After approval → execute **C.2-R1** only (pre-flight → protocol → report).  
QWO discipline: **no system mutation** during execution.

Post-execution:

1. Report `.asep/reports/C.2-R1.md` + log row
2. If PASS → `or-2-stigmata-framework` → `qualified`
3. If FAIL (promotion gap) → spawn **EWO-2 proposal** — do not fix inside C.2-R1

---

## Relationship to prior work

| Prior | Link |
|-------|------|
| C.1-R2 PASS | Structural context (cap. 5 title/role) — prerequisite |
| EWO-1 | Outline + thesis memory — partial GT for cap. 5 |
| C.1 Qualification Contract | Implicit in C.1 sections; **C.2 is canonical template** for future QWOs |

---

## Recommended next action

1. User approves this proposal
2. Operator: pre-flight → **C.2-R1** QWO (autonomous instance)
3. If FAIL + Stigmata-Framework gap → **EWO-2 proposal** → re-QWO **C.2-R2**
4. If PASS → prepare **C.3 proposal** (OR-3 corpus)
