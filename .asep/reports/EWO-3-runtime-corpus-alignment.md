# EWO-3 — Runtime Corpus Alignment Report

**Date:** 2026-06-30  
**WorkOrder:** EWO-3 · **Type:** EWO · **Category:** **Alignment**  
**Capability:** `ewo-3-runtime-corpus-alignment`  
**Verdict:** **PASS** (internal validation)  
**Lifecycle transition:** `approved` → **`implemented`**

---

## 1. Authorization

User approval with constraints:

- Promote `Bibliography-Master.md` + `Core-Theory-Map.md`
- Verify CORPUS-01…04; audit roles + author→chapter mapping
- **No** Ground Truth edit, thesis content edit, new methodological decisions
- **No** re-QWO C.3-R2 inside EWO-3

Proposal: `.asep/proposals/EWO-3-runtime-corpus-alignment.md`  
Spawned from: C.3-R1 PARTIAL (**accepted**)

---

## 2. Pre-flight

| Check | Result |
|-------|--------|
| `/health` | 200 OK |
| C.3-R1 accepted PARTIAL | ✅ |
| `Bibliography-Master.md` in runtime (before) | ❌ absent |
| `Core-Theory-Map.md` in runtime (before) | ❌ absent |
| M2 `decisions` CORPUS-01…04 | ✅ present (no PATCH required) |
| Blueprint files modified | **None** |
| QWO C.3-R2 executed | **No** |

---

## 3. Execution

**Script:** `knowledge/thesis-agent/_migration/ewo3_runtime_corpus_alignment.py` (idempotent)

| Step | Action | Result |
|------|--------|--------|
| 1 | Upload + index `Bibliography-Master.md` | id `95f2e49a-1384-4457-b57f-7e9348e23161` — **indexed**, 26 chunks |
| 2 | Upload + index `Core-Theory-Map.md` | id `8181860d-92ee-458e-b07f-d3af3743281f` — **indexed**, 99 chunks |
| 3 | Verify M2 `decisions` CORPUS-01…04 | Already aligned — **skip PATCH** |
| 4 | Role + chapter coherence audit + retrieval smoke | All checks **PASS** |

**Runtime surfaces mutated:**

| Surface | Before EWO-3 | After EWO-3 |
|---------|--------------|-------------|
| M3/M4 documents | 57 (no corpus masters) | +2 masters indexed (**59** total) |
| M2 `decisions` | CORPUS OK | unchanged |
| Blueprint repo | unchanged | unchanged |

**Corpus components now retrievable from runtime:**

- **Bibliography-Master** — 12 autori attivi, ruoli FONDAMENTALE/SUPPORTO/PERIFERICO, esclusioni
- **Core-Theory-Map** — funzione per autore, capitoli di riferimento, *quando* citare
- CORPUS-01…04 via M2 decisions (unchanged)

---

## 4. Coherence audit (Definition of Done)

| Check | Method | Result |
|-------|--------|--------|
| Bibliography-Master indexed | document status + chunks | **PASS** — 26 chunks |
| Core-Theory-Map indexed | document status + chunks | **PASS** — 99 chunks |
| CORPUS-01…04 | decisions memory substring | **PASS** |
| Role audit — Löbach FONDAMENTALE Cap.1 | `/search` from master | **PASS** |
| Role audit — Warburg FONDAMENTALE Cap.2 | `/search` from master | **PASS** |
| Role audit — Benjamin SUPPORTO Cap.2 | `/search` from master | **PASS** |
| Chapter audit — Löbach Cap.1 | `/search` from Theory Map | **PASS** |
| Chapter audit — Warburg Cap.2 | `/search` from Theory Map | **PASS** |
| Chapter audit — Albers Cap.3 | `/search` from Bibliography-Master | **PASS** |
| BIBLIOGRAPHY_MASTER retrieval | `/search` smoke | **PASS** |
| CORE THEORY MAP retrieval | `/search` smoke | **PASS** |
| Ground Truth files edited | execution log | **PASS** — none |
| New Decisions | — | **PASS** — none |

**Known residual signal (out of scope):** `Barthes_Mythologies.md` OCR remains promoted;
CORPUS-02 exclusion enforced via decisions + masters — evaluate **Applicability** at C.3-R2.

---

## 5. Capability Coverage (OR-3 post-EWO-3)

```text
Ground Truth Coverage:     100%
Runtime Coverage:          ~100%   (masters promoted; pre-flight 40% → aligned)
Qualification Coverage:    PARTIAL (C.3-R1 — pending re-QWO)
Evidence Coverage:         100%
```

Post-EWO-3, **Availability** for corpus masters is satisfied. **Completeness** remains
to be validated by re-QWO C.3-R2.

---

## 6. Lifecycle & next steps

| Field | Value |
|-------|-------|
| `ewo-3-runtime-corpus-alignment` | **`implemented`** |
| `or-3-corpus` lifecycle | **`approved`** (unchanged — not `qualified`) |
| Unblocks | re-QWO **C.3-R2** (separate authorization) |

```text
C.3-R1 PARTIAL (accepted)
        → EWO-3 implemented
        → C.3-R2 re-QWO (when authorized)
        → or-3 qualified on PASS
```

---

## 7. WO-TRACE

| Artifact | Update |
|----------|--------|
| `promotion-log.md` | EWO-3 section |
| `.asep/capabilities/thesis-agent-migration.yaml` | ewo-3 + or-3 coverage/runtime |
| `03_PROJECT/TODO.md` | EWO-3 done; C.3-R2 pending |

**No mutations:** Ground Truth, thesis chapters, QWO C.3-R1 report.
