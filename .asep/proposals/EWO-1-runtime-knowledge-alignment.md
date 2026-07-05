# Engineering WorkOrder Proposal — EWO-1

> **Status:** ✅ **APPROVED + IMPLEMENTED** (2026-06-30) — report `.asep/reports/EWO-1-runtime-knowledge-alignment.md`
>
> **Spawned from:** QWO C.1 FAIL (`.asep/reports/C.1-or-1.md`) — promotion gap, valid qualification.
>
> Program: `.asep/programs/thesis-agent-migration.yaml`

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | EWO-1 |
| **Type** | **EWO** (Engineering WorkOrder) — mutates runtime alignment only |
| **EWO category** | **Alignment** — architectural Ground Truth → promoted runtime surfaces |
| **Capability** | `ewo-1-runtime-knowledge-alignment` |
| **Lifecycle transition** | `specified` → `approved` (on proposal approval) → `implemented` (on success) |
| **Blocks** | re-QWO C.1 (`or-1-thesis-structure`); OR-2 remains blocked until OR-1 `qualified` |

---

## Objective

**Allineare il runtime al Ground Truth architetturale della tesi.**

Il QWO C.1 ha dimostrato che l'agente operativo non può ricostruire la struttura
canonica usando solo le knowledge promosse in Fase B. Questo EWO colma il gap
**senza** alterare il contenuto redazionale della tesi e **senza** nuove decisioni
editoriali.

Pattern generale (reusable): *Ground Truth (repo congelato) → promoted runtime surfaces*.
Istanza concreta oggi: `Outline-Master.md` + allineamento `thesis` memory.

---

## Evidence input (from QWO C.1)

| Finding | Source |
|---------|--------|
| OR-1 FAIL — struttura 6 cap. → 3 blocchi | `.asep/reports/C.1-or-1.md` |
| `Outline-Master.md` assente da runtime | Pre-flight + promotion audit |
| `thesis` memory incompleta vs Ground Truth | `Thesis-State.md` promosso — no cap. 4–6 architettura |
| Domanda in memory ≠ domanda in outline | GT vs Thesis-State |

---

## Scope

### In scope

1. **Promuovere** `03_PROJECT/Outline-Master.md` nel runtime (M3 document + M4 index).
2. **Aggiornare** la singleton `thesis` memory affinché includa una **mappa strutturale
   canonica** derivata fedelmente dall'outline approvato:
   - domanda generale (testo outline, non parafrasi Thesis-State)
   - elenco unità strutturali (titoli + obiettivi per capitolo/sezione outline)
   - sequenza e distinzioni esplicite (teoria cap. 1–4 vs STIGMATA cap. 5, ecc.)
3. **Allineare** `03_PROJECT/Thesis-State.md` (blueprint repo) sui soli campi
   **strutturali/metadati** incoerenti con l'outline (domanda generale, indice capitoli
   4–6 se assenti) — **senza** modificare testi di capitolo o decisioni congelate.
4. **Audit di coerenza** post-implementazione (Outline ↔ Thesis-State ↔ runtime).
5. **Log** in `promotion-log.md` + report `.asep/reports/EWO-1-runtime-knowledge-alignment.md`.

### Out of scope

- Modifica del **contenuto redazionale** della tesi (capitoli, paragrafi, argomenti).
- Nuove decisioni redazionali (`Decisions.md` — nessuna voce nuova salvo PLAT operativo
  se strettamente necessario per tracciare l'EWO).
- Re-esecuzione QWO C.1 (WorkOrder separato — **dopo** EWO-1 `implemented`).
- OR-2 … OR-7, E2E, release baseline.
- Promozione bulk di tutti i master `03_PROJECT/` (solo outline + allineamento thesis
  memory in questa istanza; altri gap → EWO futuri se emersi da QWO).

---

## Ground Truth definition

| Artifact | Role | Path (repo blueprint) |
|----------|------|------------------------|
| **Primary architectural GT** | Outline congelato v1.0 | `03_PROJECT/Outline-Master.md` |
| **Auxiliary** | Descrizione tesi (domanda/intent) | `03_PROJECT/Thesis-Description.md` |
| **Operational state** | Stato sezioni / workflow | `03_PROJECT/Thesis-State.md` |
| **Frozen decisions** | Vincoli (STIGMATA caso applicativo, ecc.) | `03_PROJECT/Decisions.md` |

Dopo EWO-1, il runtime deve permettere la ricostruzione OR-1 **senza** lettura workspace
da parte dell'agente sotto test.

---

## Implementation plan (post-approval)

| Step | Action | Surface |
|------|--------|---------|
| 1 | Upload + index `Outline-Master.md` | M3/M4 `documents` |
| 2 | Rebuild `thesis` singleton content: structural map from outline | M2 `memories` |
| 3 | Patch `Thesis-State.md` structural fields only (domanda, cap. 4–6 index) | blueprint repo |
| 4 | Re-promote or PATCH `thesis` memory if step 3 changed blueprint | M2 |
| 5 | Coherence audit script or checklist (evaluator) | report |
| 6 | Internal validation (below) | — |

**Mechanism:** extend `promote_runtime.py` or targeted API calls — idempotent, tagged
`[kimi-claw-2026-06]` / `EWO-1`. No change to QWO C.1 artifacts.

---

## Success criteria (EWO-1 done)

1. **Outline recuperabile interamente dal runtime** — document indexed; retrieval smoke
   returns structural units (6 capitoli + domanda generale outline).
2. **Nessuna divergenza materiale** tra Ground Truth (`Outline-Master.md`) e:
   - `thesis` memory (domanda + mappa capitoli/obiettivi)
   - `Thesis-State.md` (campi strutturali)
3. **Coherence audit PASS** — checklist firmata nel report EWO-1.
4. **OR-1 rieseguibile** senza dipendenze dal repository per l'agente sotto test
   (precondition for re-QWO C.1, not executed in EWO-1).

---

## Internal validation (pre re-QWO)

| Check | Method |
|-------|--------|
| Document present | `GET /documents?q=Outline` or migration tag |
| Chunks cover cap. 1–6 headings | document status `indexed`, chunk_count > 0 |
| Thesis memory domanda | equals outline § domanda generale |
| Thesis memory chapter map | 6 units with titles/objectives matching outline §1.1 dati |
| No new Decisions | `Decisions.md` diff limited to PLAT trace if any |

---

## Failure / rollback

| Risk | Mitigation |
|------|------------|
| Over-writing thesis memory editorial content | Patch adds **structural section** only; preserve existing rules refs |
| Thesis-State edit scope creep | Diff review: only domanda + chapter architecture table |
| Rollback | Restore prior memory version via API versions; revert blueprint commit; delete document row if needed |

---

## Impact analysis

| Area | Impact |
|------|--------|
| Product runtime | M2 thesis memory, M3/M4 one document — **Business/Infrastructure** |
| Architecture | None — no Constitution change |
| OR track | Unblocks **re-QWO C.1** only after `implemented` |
| OR-2+ | Remain blocked until OR-1 `qualified` |

---

## Sequence (Program)

```text
QWO C.1 ──FAIL──► Evidence (C.1-or-1.md)
                        │
                        ▼
              EWO-1 proposal ──approve──► EWO-1 execute ──implemented──►
                        │
                        ▼
              re-QWO C.1 (same proposal C.1, new run)
                        │
                   PASS ▼
              or-1 lifecycle → qualified
                        │
                        ▼
              OR-2 proposal → …
```

**QWO discipline preserved:** EWO-1 does not re-open or amend C.1 report.

---

## Deliverables

| Artifact | When |
|----------|------|
| Runtime: outline document indexed | execute |
| Runtime: thesis memory aligned | execute |
| Blueprint: `Thesis-State.md` structural sync | execute |
| `promotion-log.md` entry | execute |
| `.asep/reports/EWO-1-runtime-knowledge-alignment.md` | execute |
| `05_MEMORY/Changelog.md` entry | execute |
| Optional `Decisions.md` PLAT-07 trace | execute if needed |

---

## Approval gate

**Not authorized until explicit approval**, e.g.:

```text
EWO-1 proposal: approved
```

After approval → Inner Loop (implement → internal validation → report).
**Do not** run re-QWO C.1 in the same iteration.

---

## Relationship to Engineering Program

This EWO instantiates the general pattern **Runtime Knowledge Alignment** documented
in `docs/engineering-program.md`. Future QWO failures may spawn sibling EWOs for other
masters (Theory Map, Bibliography index, etc.) using the same proposal template.

---

## Recommended next action

User approves this proposal → operator executes EWO-1 → internal validation PASS →
spawn **re-QWO C.1** as separate approved run (no proposal change required).
