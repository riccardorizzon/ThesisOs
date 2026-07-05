# Engineering WorkOrder Proposal — EWO-3

> **Status:** ✅ **APPROVED + IMPLEMENTED** (2026-06-30) — report `.asep/reports/EWO-3-runtime-corpus-alignment.md`
>
> **Spawned from:** QWO C.3-R1 PARTIAL (accepted) — `.asep/reports/C.3-R1.md`
>
> **EWO category:** **Alignment** (Runtime Corpus Alignment)
>
> Program: `.asep/programs/thesis-agent-migration.yaml`

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | EWO-3 |
| **Type** | **EWO** — mutates runtime alignment only |
| **EWO category** | **Alignment** — corpus Ground Truth → promoted runtime surfaces |
| **Capability** | `ewo-3-runtime-corpus-alignment` |
| **Lifecycle transition** | `draft` → **`approved`** → `implemented` (on success) |
| **Blocks** | re-QWO C.3-R2 (`or-3-corpus`); OR-4 until OR-3 `qualified` |
| **Pattern** | Same as EWO-1/2: Ground Truth masters → M3/M4 promotion |

---

## Objective

**Allineare il runtime al Ground Truth del corpus teorico congelato.**

C.3-R1 (PARTIAL, accepted) ha dimostrato **Applicability** corretta (CORPUS-02/03) ma
**Completeness** insufficiente: `Bibliography-Master.md` e `Core-Theory-Map.md` assenti dal
runtime. Questo EWO colma il gap senza alterare Ground Truth, contenuti tesi, o nuove decisioni.

---

## Evidence input (from QWO C.3-R1)

| Finding | Source |
|---------|--------|
| OR-3 PARTIAL — 6/12 autori; esclusioni OK | `.asep/reports/C.3-R1.md` |
| Applicability PASS — Mythologies escluso | C.3-R1 § Availability vs Applicability |
| Masters non promossi | Pre-flight 40% runtime coverage |
| Löbach/Csikszentmihalyi assenti nonostante libri OCR | Agent + promotion gap |
| C.3-R1 **ACCEPTED** | Outer Loop 2026-06-30 |

---

## Scope (authorized)

### In scope

1. **Promuovere** `03_PROJECT/Bibliography-Master.md` v1.0 → M3/M4
2. **Promuovere** `03_PROJECT/Core-Theory-Map.md` v2.1 → M3/M4
3. **Verificare** M2 `decisions` espone CORPUS-01…04 fedelmente (PATCH solo se drift)
4. **Audit coerenza** post-promozione:
   - Ruoli FONDAMENTALE / SUPPORTO / PERIFERICO vs master
   - Mapping autore → capitolo (Löbach cap.1, Warburg cap.2, …)
   - Retrieval smoke da artefatti promossi (non homonyms)
5. **Log** `promotion-log.md` + report `.asep/reports/EWO-3-runtime-corpus-alignment.md`
6. **Script idempotente** `ewo3_runtime_corpus_alignment.py`

### Out of scope

- Modifica Ground Truth (`Bibliography-Master`, `Core-Theory-Map`, `Decisions.md`)
- Modifica contenuti redazionali tesi
- Nuove decisioni metodologiche
- Ridefinizione corpus / nuovi autori
- Normalizzazione `Barthes_Mythologies.md` (separate decision)
- re-QWO C.3-R2 **dentro** questo EWO
- OR-4 … E2E

---

## Ground Truth definition

| Artifact | Role | Path |
|----------|------|------|
| **Primary** | Bibliografia attiva v1.0 | `03_PROJECT/Bibliography-Master.md` |
| **Primary** | Corpus teorico v2.1 | `03_PROJECT/Core-Theory-Map.md` |
| **Binding** | CORPUS-01…04 | `03_PROJECT/Decisions.md` |
| **Auxiliary** | Books OCR, Tesi-bibliografia | già promossi Fase B |

Post-EWO-3, runtime Coverage target **~100%** for OR-3 GT elements; re-QWO C.3-R2 validates **Completeness**.

---

## Success criteria

1. Both masters **indexed** with chunks > 0
2. CORPUS-01…04 verified in M2 decisions
3. Coherence audit PASS — roles + chapter mapping retrievable from promoted masters
4. No blueprint files edited
5. `or-3-corpus` remains **`approved`** until C.3-R2 PASS

---

## WO-TRACE

```text
C.3-R1 PARTIAL (accepted)
        → EWO-3 approved
        → EWO-3 execute → implemented
        → C.3-R2 re-QWO (separate authorization)
```
