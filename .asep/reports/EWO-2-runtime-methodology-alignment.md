# EWO-2 — Runtime Methodology Alignment Report

**Date:** 2026-06-30  
**WorkOrder:** EWO-2 · **Type:** EWO · **Category:** **Alignment**  
**Capability:** `ewo-2-runtime-methodology-alignment`  
**Verdict:** **PASS** (internal validation)  
**Lifecycle transition:** `draft` → `approved` → **`implemented`**

---

## 1. Authorization

User approval with constraints:

- Promote methodology + document structures; coherence audit
- Structural memory update **only if required**
- **No** Ground Truth edit, methodology redefinition, new decisions, framework extension
- **No** re-QWO C.2-R2 inside EWO-2

Proposal: `.asep/proposals/EWO-2-runtime-methodology-alignment.md`  
Spawned from: C.2-R1 PARTIAL (accepted)

---

## 2. Pre-flight

| Check | Result |
|-------|--------|
| `/health` | 200 OK |
| C.2-R1 accepted PARTIAL | ✅ |
| `Stigmata-Framework.md` in runtime (before) | ❌ absent |
| `Decisions.md` METH-02/METH-04 in M2 | ✅ present (no PATCH required) |
| Blueprint files modified | **None** (constraint) |
| QWO C.2-R2 executed | **No** |

---

## 3. Execution

**Script:** `knowledge/thesis-agent/_migration/ewo2_runtime_methodology_alignment.py` (idempotent)

| Step | Action | Result |
|------|--------|--------|
| 1 | Upload + index `Stigmata-Framework.md` | id `e7540d4e-b54e-4217-9d53-92cfba4b3f97` — **indexed**, 49 chunks |
| 2 | Verify M2 `decisions` METH-02/METH-04 | Already aligned — **skip PATCH** |
| 3 | PATCH `thesis` memory | **Not required** — no structural drift; blueprint unchanged per constraint |
| 4 | Coherence audit + retrieval smoke | All checks **PASS** |

**Runtime surfaces mutated:**

| Surface | Before EWO-2 | After EWO-2 |
|---------|--------------|-------------|
| M3/M4 documents | 56 (no Stigmata-Framework) | +1 framework indexed (57 total) |
| M2 `decisions` | METH-02/04 OK | unchanged |
| M2 `thesis` | v4 | unchanged |
| Blueprint repo | unchanged | unchanged |

**Methodology components now retrievable from runtime:**

- §1 **DOCUMENTATION_MASTER** (BZ, MB, CP, WP, …)
- §2 **EVIDENCE MATRIX**
- **Livelli evidenza:** FONDATO, PLAUSIBILE, NON VERIFICABILE, APPLICAZIONE TESI
- Workflow evidence-first (in framework body)

---

## 4. Coherence audit (Definition of Done)

| Check | Method | Result |
|-------|--------|--------|
| Framework indexed | document status + chunks | **PASS** — 49 chunks |
| METH-02 | decisions memory substring | **PASS** |
| METH-04 | decisions memory substring | **PASS** |
| DOCUMENTATION_MASTER retrievable | `/search` smoke | **PASS** — 5 hits |
| EVIDENCE MATRIX retrievable | `/search` smoke | **PASS** — 5 hits |
| Evidence levels retrievable | `/search` smoke | **PASS** — 5 hits |
| STIGMATA role (caso applicativo) | `/search` smoke | **PASS** — 5 hits |
| Ground Truth files edited | git / execution log | **PASS** — none |
| New Decisions | — | **PASS** — none |

**Audit verdict:** **PASS**

---

## 5. Evidence (script log)

```text
health: OK
framework uploaded: status=indexed chunks=49
decisions memory: present len=4502
  check framework indexed: PASS (indexed)
  check framework chunks: PASS (49)
  check METH-02 in decisions: PASS ()
  check METH-04 in decisions: PASS ()
  check retrieval DOCUMENTATION_MASTER: PASS (5 hits)
  check retrieval EVIDENCE MATRIX: PASS (5 hits)
  check retrieval evidence levels: PASS (5 hits)
  check retrieval METH-02 role: PASS (5 hits)
```

---

## 6. Out of scope (confirmed not executed)

- re-QWO C.2-R2
- Blueprint / Ground Truth edits
- New `Decisions.md` entries
- Thesis memory PATCH (not required)
- OR-3 … E2E

---

## 7. Impact on capability graph

| Capability | Before | After EWO-2 |
|------------|--------|-------------|
| `ewo-2-runtime-methodology-alignment` | `draft` / `ready` | **`implemented` / `done`** |
| `or-2-stigmata-framework` | `approved` / blocked | `approved` / **`ready`** for C.2-R2 |

**OR-2 remains `approved`, not `qualified`** until re-QWO C.2-R2 PASS.

---

## 8. Recommended next step

```text
EWO-2 PASS ✅
        ↓
Validation EWO-2 (this report)
        ↓
re-QWO C.2-R2 (separate autonomous QWO — user approval)
        ↓
PASS → or-2 qualified → C.3 proposal
```

---

## 9. Artifacts

| Artifact | Path |
|----------|------|
| Execution script | `knowledge/thesis-agent/_migration/ewo2_runtime_methodology_alignment.py` |
| Ground Truth (unchanged) | `knowledge/thesis-agent/03_PROJECT/Stigmata-Framework.md` |
| Promotion log | `knowledge/thesis-agent/_migration/promotion-log.md` |
| Spawned-from QWO | `.asep/reports/C.2-R1.md` |
