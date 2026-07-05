# Qualification WorkOrder Proposal — C.3

> **Status:** ✅ **Approved** — pre-flight audit complete (`.asep/reports/C.3-preflight-runtime-audit.md`)
>
> **Measured Runtime Coverage:** **40%** (not ~58%) — masters absent; books promoted.
>
> Program: `.asep/programs/thesis-agent-migration.yaml`  
> Spec base: `knowledge/thesis-agent/_migration/operational-readiness.md` § OR-3  
> Template: `.asep/templates/qualification-work-order-template.md` (Qualification Contract)

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | C.3 |
| **Type** | **QWO** (Qualification WorkOrder) — validation only |
| **Capability** | `or-3-corpus` |
| **Lifecycle transition** | `specified` → `approved` (on proposal approval) → `qualified` (on PASS) |
| **Program** | `thesis-agent-migration` · run `kimi-claw-2026-06` |
| **Depends on** | `or-2-stigmata-framework` **qualified** (C.2-R2 PASS, 2026-06-30) |
| **First run id** | `C.3-R1` (on approval) |

---

## Objective

Dimostrare che il **runtime ThesisOS vivo** elenca e spiega correttamente il **corpus
bibliografico attivo** congelato — autori, opere, capitoli di tesi, ruolo
(fondamentale/supporto/periferico), **quando** citare ciascuna fonte, ed **esclusioni**
documentate — senza proporre nuove fonti non classificate, usando **esclusivamente**
knowledge promossa.

Non verifica l'esistenza fisica di PDF/libri (OCR in `04_KNOWLEDGE/Books/` già promosso
parzialmente). Verifica che l'agente operativo conosca la **mappa del corpus** congelata.

---

## Capability Coverage (pre-flight audit — measured)

Observability metric — **does not replace** QWO verdict. Full audit:
`.asep/reports/C.3-preflight-runtime-audit.md`. See `docs/engineering-program.md`
§ Capability Coverage.

| Dimension | OR-3 (measured pre-flight) | Notes |
|-----------|----------------------------|-------|
| **Ground Truth Coverage** | **100%** | All GT files in repo |
| **Runtime Coverage** | **40%** | Masters absent; 8 books promoted |
| **Qualification Coverage** | *pending* | No QWO run yet |
| **Evidence Coverage** | *pending* | No report yet |

**Runtime Coverage breakdown (measured — artifact-strict):**

| GT element | Promoted | Indexed | Search from artifact | Credit |
|------------|----------|---------|----------------------|--------|
| `Bibliography-Master.md` | ❌ | ❌ | ❌ | 0% / 35% |
| `Core-Theory-Map.md` | ❌ | ❌ | ❌ | 0% / 25% |
| `Decisions.md` CORPUS | ✅ M2 | ✅ | ✅ | 25% |
| Book OCR (8 files) | ✅ 8/8 | ✅ | ✅ | 10% |
| `Tesi-bibliografia-completa.md` | ✅ | ✅ | ✅ | 5% |

**Total Runtime Coverage: 40%**

**Known runtime noise:** Fase B promoted `Barthes_Mythologies.md` — **CORPUS-02 excluded**.
Agent under test may see conflicting signal; PASS requires citing **exclusion** from
decisions/master, not treating Mythologies as active.

**Reference (qualified capability OR-2 post EWO-2 + C.2-R2):**

| Dimension | OR-2 |
|-----------|------|
| Ground Truth Coverage | 100% |
| Runtime Coverage | 100% |
| Qualification Coverage | 100% (PASS) |
| Evidence Coverage | 100% |

---

## Qualification Contract

### Capability

`or-3-corpus` — OR-3 corpus and exclusions.

### Prerequisiti

| Precondition | Expected state | Verification |
|--------------|----------------|--------------|
| `or-2` qualified | C.2-R2 PASS | capability graph |
| EWO-1, EWO-2 implemented | outline + STIGMATA methodology in runtime | EWO reports |
| Phase A / B | UNI-01, REL-01; books + decisions promoted | `promotion-log.md` |
| Live stack | `/health` → 200 | pre-flight |
| Proposal approved | this document → approved | **User explicit approval** |

### Ground Truth

| Priority | Artifact | Role |
|----------|----------|------|
| **Primary** | `03_PROJECT/Bibliography-Master.md` v1.0 | Elenco autori attivi, opere, capiti, livello FONDAMENTALE/SUPPORTO, sezione esclusi |
| **Primary** | `03_PROJECT/Core-Theory-Map.md` v2.1 | Funzione per autore, capitolo di uso, *quando* citare, corpus minimo |
| **Binding** | `03_PROJECT/Decisions.md` | CORPUS-01 (~12 autori), CORPUS-02 (Barthes *Mythologies* escluso), CORPUS-03 (Bourriaud escluso), CORPUS-04 (library-first) |
| **Auxiliary** | `04_KNOWLEDGE/Books/*.md` (OCR) | Testo fonte se routed; non sostituisce master |
| **Auxiliary** | `Tesi-bibliografia-completa.md` | Indice operativo; subordinato ai master congelati |

**Corpus attivo (GT — 12 autori, CORPUS-01):**

| # | Autore | Ruolo GT | Capitoli (sintesi) |
|---|--------|----------|---------------------|
| 1 | Löbach | FONDAMENTALE | Cap. 1 — struttura processo |
| 2 | Csikszentmihalyi | FONDAMENTALE | Cap. 1 — flow / esperienza |
| 3 | Sennett | FONDAMENTALE | Cap. 4 — pratica manuale |
| 4 | Warburg | FONDAMENTALE | Cap. 2 — ricerca / memoria visiva |
| 5 | Albers | SUPPORTO | Cap. 3 — colore |
| 6 | Hollander | SUPPORTO | Cap. 3 — silhouette / corpo |
| 7 | Barthes | SUPPORTO | Cap. 3 — *Il sistema della moda* (non Mythologies) |
| 8 | Dorfles | SUPPORTO | Cap. 3 — norma/deviazione |
| 9 | Eco | SUPPORTO | Cap. 3 — estetica del difetto |
| 10 | Benjamin | SUPPORTO | Cap. 2 — aura / riproduzione |
| 11 | Seivewright | SUPPORTO | Cap. 2 — ricerca operativa |
| 12 | Flügel | PERIFERICO | Supporto contestuale (non pilastro) |

**Esclusioni obbligatorie (GT):**

| ID | Escluso | Motivo (GT) |
|----|---------|-------------|
| CORPUS-02 | Barthes *Mythologies* | Decisione congelata — non corpus attivo |
| CORPUS-03 | Bourriaud / estetica relazionale | Decisione congelata — non pilastro |

**Elementi GT obbligatori per PASS:**

1. Elenco **completo** dei ~12 autori attivi con opera principale e ruolo.
2. Per autori **fondamentali**: indica **quando**/capitolo di citazione (coerente con Theory Map / Bibliography-Master).
3. **Esclusioni** Barthes *Mythologies* e Bourriaud con riferimento a decisione congelata.
4. **Non** propone nuove fonti come attive senza classificazione «candidate».
5. Distingue FONDAMENTALE vs SUPPORTO (e Flügel periferico se menzionato).
6. Coerente con CORPUS-04 (library-first) se citato nel contesto corpus.

### Runtime Boundary

**Agent under test must NOT use:**

- File workspace `knowledge/thesis-agent/`
- Export `_inbox/kimi-claw/`
- Web / external sources
- Operator paste of bibliography from clipboard
- File attachments on `/chat`

**Allowed runtime surfaces (only):**

| Surface | Expected contribution |
|---------|----------------------|
| M2 `decisions` | CORPUS-01…04 |
| M2 `editable` | Regole corpus, library-first |
| M3/M4 documents | Books OCR, `Tesi-bibliografia-completa`, **if promoted:** Bibliography-Master, Core-Theory-Map |
| M3/M4 outline / STIGMATA | Context only — not substitute for corpus map |

**Hard operator constraint:** single POST `/chat`, **new** `conversation_id`, canonical prompt only.

### Evidence Required

| Artifact | Content |
|----------|---------|
| `.asep/reports/C.3-R1.md` | Pre-flight + **Capability Coverage** snapshot, prompt, output, oracle diff, verdict |
| `operational-readiness-log.md` | Row `C.3-R1`, OR-3 column |
| Capability graph | Update `coverage` + `qualification_runs[]` on conclusion |

Run history immutable (`C.3-R2`, …).

### PASS Criteria

Output fedele al Ground Truth, ricostruibile dalle sorgenti promosse:

1. ~**12 autori attivi** elencati con opera e ruolo.
2. **Capitoli / quando citare** per fondamentali e supporti chiave (Löbach cap.1, Albers cap.3, Warburg cap.2, …).
3. **Barthes *Mythologies*** e **Bourriaud** esclusi con motivazione CORPUS-02/03.
4. Barthes attivo = ***Il sistema della moda***, non Mythologies.
5. Nessuna fonte nuova presentata come attiva senza «candidate».
6. Nessuna contraddizione materiale vs master congelati.
7. Output autosufficiente; runtime boundary rispettato.

→ `or-3-corpus` lifecycle → **`qualified`**; OR-4 unblocked (C.4 proposal).

### PARTIAL Criteria

- Sottoinsieme autori corretto + esclusioni OK, ma mappa capiti/ruoli incompleta.
- Elenco autori da libri OCR ma master (Bibliography-Master / Theory Map) assenti in output.
- Causa: **agent limitation** vs **promotion gap** — document in report.
- **Non** avanza lifecycle senza decisione utente.

### FAIL Criteria

- Autori mancanti o inventati; esclusioni assenti o invertite.
- Mythologies o Bourriaud trattati come corpus attivo.
- Propone espansione corpus non classificata.
- Impossibilità ricostruire GT dalle sole sorgenti promosse → *promotion gap*.
- Violazione runtime boundary.

### Spawn Rule (eventuale EWO)

```text
QWO C.3-Rk → FAIL or PARTIAL (promotion gap)
        → Evidence + Coverage snapshot
        → EWO proposal (e.g. EWO-3: Corpus Alignment)
        → NO patch during QWO
        → re-QWO C.3-R{k+1}
```

**Likely promotion gap (pre-approval audit):** `Bibliography-Master.md` and
`Core-Theory-Map.md` **not** in runtime M3/M4. Valid FAIL/PARTIAL per WO-TRACE —
pattern identical to C.1/C.2.

**Candidate EWO-3 (if gap confirmed):** **Alignment** — promote corpus masters +
audit CORPUS decisions; optional normalization note on Mythologies OCR doc (separate
scope decision). **Not part of C.3 QWO.**

### Lifecycle Transition

| Verdict | Capability lifecycle | OR-3 log | Unblocks |
|---------|---------------------|----------|----------|
| **PASS** | → **`qualified`** | PASS | `or-4-rules` (C.4) |
| **PARTIAL** | unchanged (`specified`→`approved`) | PARTIAL | Outer Loop |
| **FAIL** | unchanged | FAIL | EWO proposal if structural |

Post-QWO: update **Capability Coverage** on capability graph (WO-TRACE).

---

## Scope

### In scope (after approval)

- Pre-flight: inventory + **Coverage snapshot**
- Execute **C.3-R1**: live `/chat`, canonical prompt
- Evaluate vs Qualification Contract
- Report + log + coverage update

### Out of scope

- No knowledge/memory/documents mutations during QWO
- No OR-4 … E2E
- No EWO-3 execution inside C.3 proposal approval (separate WO)

---

## Test protocol

### Canonical prompt (OR-3)

```text
Elenca gli autori del corpus attivo. Per ciascuno: opera, capitolo/i tesi, ruolo
(fondamentale/supporto). Indica cosa è escluso e perché.
```

### Evaluation oracle (evaluator only)

Diff output vs Bibliography-Master + Core-Theory-Map + Decisions. Classify gap cause.
Update Capability Coverage dimensions in report.

---

## Impact analysis

| Area | Impact |
|------|--------|
| Architecture | None |
| Runtime | None during QWO |
| Capability lifecycle | `or-3` → `qualified` on PASS only |
| Program | Unblocks OR-4 on PASS |
| Risk | Promotion gap on corpus masters (~58% runtime coverage) |

---

## Rollback

N/A — log/report only.

---

## Approval gate

**Not authorized until explicit approval**, e.g.:

```text
C.3 proposal: approved
```

After approval → **C.3-R1** only. QWO discipline: **no system mutation**.

---

## Recommended next action

1. User approves this proposal
2. Execute **C.3-R1** (expect possible PARTIAL/FAIL → EWO-3 Alignment)
3. If PASS → **C.4 proposal** (OR-4 rules)
