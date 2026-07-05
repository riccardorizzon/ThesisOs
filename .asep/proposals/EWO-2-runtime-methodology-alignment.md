# Engineering WorkOrder Proposal — EWO-2

> **Status:** ✅ **APPROVED + IMPLEMENTED** (2026-06-30) — report `.asep/reports/EWO-2-runtime-methodology-alignment.md`
>
> **Spawned from:** QWO C.2-R1 PARTIAL (`.asep/reports/C.2-R1.md`) — promotion gap, valid qualification.
>
> **EWO category:** **Alignment** (Runtime Methodology Alignment)
>
> Program: `.asep/programs/thesis-agent-migration.yaml`

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | EWO-2 |
| **Type** | **EWO** (Engineering WorkOrder) — mutates runtime alignment only |
| **EWO category** | **Alignment** — Ground Truth metodologico → promoted runtime surfaces |
| **Capability** | `ewo-2-runtime-methodology-alignment` |
| **Lifecycle transition** | `draft` → `approved` (on proposal approval) → `implemented` (on success) |
| **Blocks** | re-QWO C.2-R2 (`or-2-stigmata-framework`); OR-3 remains blocked until OR-2 `qualified` |
| **Pattern** | Same as EWO-1: capability-oriented, not file-oriented — extensible if methodology docs grow |

---

## Objective

**Promuovere nel runtime la metodologia completa che governa STIGMATA come caso applicativo.**

Il QWO C.2-R1 ha dimostrato che l'agente possiede il **modello concettuale** (METH-02, cap. 5,
evidence-first) dalle sorgenti già promosse, ma **non** l'infrastruttura documentale congelata
(DOCUMENTATION_MASTER, EVIDENCE MATRIX, livelli di evidenza) perché `Stigmata-Framework.md`
non è nel runtime M3/M4.

Questo EWO colma il gap **senza** alterare contenuti redazionali della tesi e **senza** nuove
decisioni metodologiche.

**Reusable pattern:** *Methodology Ground Truth (repo) → promoted runtime surfaces*.

---

## Evidence input (from QWO C.2-R1)

| Finding | Source |
|---------|--------|
| OR-2 PARTIAL — ruolo STIGMATA + cap. 5 OK | `.asep/reports/C.2-R1.md` |
| DOCUMENTATION_MASTER non recuperabile | Output vs GT diff |
| EVIDENCE MATRIX / livelli evidenza assenti | Output vs GT diff |
| `Stigmata-Framework.md` assente da runtime | Pre-flight C.2-R1 |
| Agent reframed framework as outline §5 narrative | Secondary — promotion gap primary |
| C.2-R1 **ACCEPTED** as PARTIAL | Outer Loop 2026-06-30 |

---

## Scope

### In scope

1. **Promuovere** `03_PROJECT/Stigmata-Framework.md` v1.0 nel runtime (M3 document + M4 index).
   - Include per design congelato:
     - **§1 DOCUMENTATION_MASTER** (tassonomia materiale: BZ, MB, CP, WP, FT, FF, TC, AD, …)
     - **§2 EVIDENCE MATRIX** (materiale ↔ concetti teorici)
     - **Livelli di evidenza** (FONDATO, PLAUSIBILE, NON VERIFICABILE, APPLICAZIONE TESI)
     - Workflow evidence-first (§ workflow in framework)
2. **Audit di coerenza** post-promozione:
   - Framework ↔ `Decisions.md` **METH-02** (caso applicativo)
   - Framework ↔ **METH-04** (evidence-first)
   - Framework ↔ `Outline-Master.md` § Cap. 5 (lettura analitica, non autobiografica)
   - Runtime retrieval smoke: DOCUMENTATION_MASTER, EVIDENCE MATRIX, livelli evidenza
3. **Allineamento memory (strutturale only, se necessario):**
   - Verificare M2 `decisions` espone METH-02/METH-04 fedelmente
   - Opzionale PATCH `thesis` memory: riferimento runtime a framework promosso (metadati
     artefatto — **no** testo di capitolo)
4. **Log** `promotion-log.md` + report `.asep/reports/EWO-2-runtime-methodology-alignment.md`
5. **Script idempotente** `ewo2_runtime_methodology_alignment.py` (pattern EWO-1)

### Out of scope

- Modifica **contenuti redazionali** tesi (capitoli, paragrafi STIGMATA scritti)
- Nuove decisioni metodologiche in `Decisions.md` (salvo traccia PLAT operativa se strettamente necessaria)
- Popolamento materiale binario STIGMATA (`04_KNOWLEDGE/STIGMATA/` — ancora vuoto per design)
- Re-esecuzione QWO C.2-R2 **dentro** questo EWO
- OR-3 … OR-7, E2E, release baseline
- Promozione bulk di tutti i master `03_PROJECT/` (solo metodologia STIGMATA in questa istanza)

---

## Ground Truth definition

| Artifact | Role | Path (repo blueprint) |
|----------|------|------------------------|
| **Primary methodology GT** | Framework documentale STIGMATA v1.0 | `03_PROJECT/Stigmata-Framework.md` |
| **Binding decisions** | METH-02, METH-04, REV-006 | `03_PROJECT/Decisions.md` |
| **Structural context** | Cap. 5 ruolo e vincoli analitici | `03_PROJECT/Outline-Master.md` § Cap. 5 |
| **Auxiliary** | Regole progetto evidence-first | `03_PROJECT/Project-Rules.md`, `05_MEMORY/Permanent.md` |

Dopo EWO-2, il runtime deve permettere OR-2 **PASS** su C.2-R2 senza lettura workspace
da parte dell'agente sotto test.

**Nota:** DOCUMENTATION_MASTER, EVIDENCE MATRIX e livelli evidenza **vivono** in
`Stigmata-Framework.md` — una promozione documentale indicizzata copre l'infrastruttura;
l'audit verifica recuperabilità per sezione, non file separati.

---

## Implementation plan (post-approval)

| Step | Action | Surface |
|------|--------|---------|
| 1 | Upload + index `Stigmata-Framework.md` | M3/M4 `documents` |
| 2 | Verify M2 `decisions` vs METH-02/METH-04; PATCH if material drift | M2 |
| 3 | Optional PATCH `thesis` memory — framework promoted flag / artefatto runtime | M2 |
| 4 | Coherence audit + retrieval smoke (DOCUMENTATION_MASTER, EVIDENCE MATRIX, FONDATO/PLAUSIBILE/NON VERIFICABILE) | script + report |
| 5 | Internal validation checklist | report |

**Mechanism:** `ewo2_runtime_methodology_alignment.py` — idempotent, tagged
`[kimi-claw-2026-06]` / `EWO-2`. No mutation of C.2-R1 QWO artifacts.

---

## Success criteria (EWO-2 done)

1. **Stigmata-Framework recuperabile interamente dal runtime** — document `indexed`;
   chunk_count > 0; retrieval returns DOCUMENTATION_MASTER headings and evidence levels.
2. **Nessuna divergenza materiale** tra Ground Truth e:
   - contenuto indicizzato (sezioni §1–§2 + legenda evidenza)
   - coerenza METH-02/METH-04 in `decisions` memory
3. **Coherence audit PASS** — checklist firmata nel report EWO-2.
4. **OR-2 rieseguibile** (precondition C.2-R2, not executed in EWO-2).

---

## Internal validation (pre re-QWO)

| Check | Method |
|-------|--------|
| Document present | `GET /documents` — `Stigmata-Framework.md` |
| Sections indexed | status `indexed`; chunks cover `# 1. DOCUMENTATION_MASTER`, `# 2. EVIDENCE MATRIX` |
| Evidence levels retrievable | `/search` smoke: FONDATO PLAUSIBILE NON VERIFICABILE |
| METH-02 in decisions memory | substring audit vs `Decisions.md` |
| METH-04 evidence-first | substring audit |
| No new editorial Decisions | diff limited to PLAT trace if any |

---

## Failure / rollback

| Risk | Mitigation |
|------|------------|
| Over-writing editorial content | Document upload only; memory PATCH structural refs only |
| Thesis-State scope creep | No chapter text changes |
| Rollback | Delete document row; restore memory version via API versions |

---

## Impact analysis

| Area | Impact |
|------|--------|
| Product runtime | M3/M4 one document; optional M2 PATCH — Infrastructure/Business |
| Architecture | None — no Constitution change |
| OR track | Unblocks **re-QWO C.2-R2** only after `implemented` |
| OR-3+ | Remain blocked until OR-2 `qualified` |

---

## Sequence (Program)

```text
C.2-R1 PARTIAL (accepted) ──► Evidence (C.2-R1.md)
                        │
                        ▼
              EWO-2 proposal ──approve──► EWO-2 execute ──implemented──►
                        │
                        ▼
              re-QWO C.2-R2 (same proposal C.2, new run)
                        │
                   PASS ▼
              or-2 lifecycle → qualified
                        │
                        ▼
              C.3 proposal → …
```

**QWO discipline preserved:** EWO-2 does not re-open or amend C.2-R1 report.

---

## Deliverables

| Artifact | When |
|----------|------|
| Runtime: `Stigmata-Framework.md` indexed | execute |
| Runtime: decisions/thesis aligned (if needed) | execute |
| `ewo2_runtime_methodology_alignment.py` | execute |
| `promotion-log.md` entry | execute |
| `.asep/reports/EWO-2-runtime-methodology-alignment.md` | execute |
| `05_MEMORY/Changelog.md` entry | execute |

---

## Approval gate

Outer Loop authorized **spawn** with approved scope (2026-06-30).

**Execution not authorized** until explicit approval, e.g.:

```text
EWO-2 proposal: approved
```

After approval → Inner Loop (implement → internal validation → report).
**Do not** run re-QWO C.2-R2 in the same iteration.

---

## Relationship to Engineering Program

- **EWO category:** Alignment (see `docs/engineering-program.md` § EWO categories)
- Sibling: EWO-1 (architectural alignment — outline)
- Instance pattern: Runtime Methodology Alignment — reusable for future methodology masters

---

## Recommended next action

User approves execution → operator runs EWO-2 → internal validation PASS →
spawn **re-QWO C.2-R2** as separate approved run.
