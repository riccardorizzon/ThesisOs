# EWO-4 — Runtime Grounding Alignment Report

**Date:** 2026-06-30  
**WorkOrder:** EWO-4 · **Type:** EWO · **Category:** **Grounding** (new)  
**Capability:** `ewo-4-runtime-grounding-alignment`  
**Verdict:** **PASS** (internal validation)  
**Lifecycle:** `approved` → **`implemented`**

**Spawned from:** `.asep/reports/C.3-R2-investigation.md` (investigation **ACCEPTED**)  
**Operator:** EWO-4 proposal **APPROVED** — Grounding category

---

## 1. Authorization

- Align grounding pipeline with binding M2 decisions
- Prompt hierarchy, exclusion-aware retrieval merge
- **No** Ground Truth edit, thesis content edit, new decisions
- **No** re-QWO C.3-R3 inside EWO-4

Proposal: `.asep/proposals/EWO-4-runtime-grounding-alignment.md`

---

## 2. Problem (investigation recap)

| Class | Finding |
|-------|---------|
| **Grounding Gap** | `decisions` not in prompt; grounding instruction denied non-source answers |
| **Ranking Gap** | OR-3 query top-10 lacked exclusion chunks |
| **NOT Promotion Gap** | Runtime Coverage ~100% |

---

## 3. Implementation (Grounding layer)

| Change | Path | Effect |
|--------|------|--------|
| Load binding `decisions` into prompt context | `backend/app/schemas/memory.py`, `services/memory/service.py` | M2 CORPUS in `[BINDING DECISIONS]` prefix |
| Render binding section first | `services/memory/render.py` | Decisions override contradictory sources |
| Grounding instruction hierarchy | `graph/prompt_wire.py` | Apply CORPUS exclusions even if OCR present in `[n]` |
| Exclusion-aware retrieval merge | `graph/retriever.py` | Secondary boost query for corpus/exclusion prompts |
| Unit tests | `tests/test_grounding.py`, `test_memory_render.py`, `test_retriever_exclusion.py` | 9 tests PASS |

**Cognitive pipeline level mutated:** **Grounding** (+ **Retrieval** merge helper)

**Not mutated:** Ground Truth repo, thesis chapters, `Decisions.md` content, M2 row text

---

## 4. Coherence audit

**Script:** `knowledge/thesis-agent/_migration/ewo4_runtime_grounding_alignment.py`

| Check | Result |
|-------|--------|
| `/health` | PASS |
| M2 `decisions` CORPUS-01…04 | PASS |
| Exclusion search smoke | PASS (5 hits) |
| Unit tests (grounding) | PASS (9) |

---

## 5. Live stack note

Code changes are in the repository. **Restart the backend** (e.g. `make up` / docker compose) before **C.3-R3** so the live graph loads EWO-4 grounding.

---

## 6. Lifecycle & next steps

| Field | Value |
|-------|-------|
| `ewo-4-runtime-grounding-alignment` | **`implemented`** |
| `or-3-corpus` | **`approved`** — ready for **C.3-R3** re-QWO |
| FAIL disposition | EWO remediation applied — re-QWO authorized under Level 2 (QC required) |

```text
C.3-R2 FAIL → INVESTIGATE (ACCEPTED) → EWO-4 Grounding → C.3-R3 (pending)
```

---

## 7. WO-TRACE

| Artifact | Update |
|----------|--------|
| `promotion-log.md` | EWO-4 section (code path — no new docs) |
| `.asep/capabilities/thesis-agent-migration.yaml` | `ewo-4` node |
| `docs/engineering-program.md` | Grounding category + cognitive pipeline |

**No mutations:** QWO reports, Ground Truth, investigation report content.
