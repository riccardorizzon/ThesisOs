# Investigation Report — C.3-R2 FAIL

> **Disposition:** `C.3-R2 FAIL: INVESTIGATE` — **ACCEPTED** (operator 2026-06-30)  
> **Classification (operator binding):**
> ```text
> Primary:   Grounding Gap
> Secondary: Ranking Gap
> Tertiary:  Model Variance
> Structural Promotion Gap: REJECTED
> ```
> **Remediation:** EWO-4 **Grounding** — **APPROVED + implemented** (`.asep/reports/EWO-4-runtime-grounding-alignment.md`)  
> **Validation:** C.3-R3 PARTIAL — Applicability restored; see `.asep/reports/C.3-R3.md`

---

## Executive summary

| Field | Value |
|-------|-------|
| **Primary cause class** | **Grounding Gap** (Runtime) |
| **Secondary** | **Ranking Gap** (Runtime) + **Model Variance** (Behavioral) |
| **Ruled out** | **Promotion Gap** (Structural) |
| **Confidence** | **High** (code path + retrieval simulation + run diff) |
| **Recommended next WO** | **EWO Infrastructure / Runtime** — not Alignment |

---

## Cause classification

```text
Cause Classification

Primary:     Grounding Gap (Runtime layer)
Secondary:   Ranking Gap (Runtime layer)
Tertiary:      Model Variance (Behavioral layer)

NOT:         Promotion Gap
NOT:         Governance Gap (QC/Policy operated correctly)

Confidence:  HIGH
Evidence:    prompt_wire.py instruction; PROMPT_CONTEXT_KINDS;
             retrieval simulation; C.3-R1 vs C.3-R2 output diff
```

### FAIL taxonomy (framework)

| Class | This investigation |
|-------|-------------------|
| **Structural** | ❌ Ruled out — masters indexed; Runtime Coverage ~100% |
| **Runtime** | ✅ **Primary** — grounding prompt + retrieval ranking |
| **Behavioral** | ⚠️ Secondary — run-to-run synthesis variance |
| **Governance** | ❌ Level 2 STOP was correct |

---

## Evidence chain

### 1. Availability — exclusions ARE in runtime

| Surface | CORPUS-02/03 available? | Evidence |
|---------|-------------------------|----------|
| M2 `decisions` memory | ✅ | API: `CORPUS-01…04`, `Mythologies`, `Bourriaud` in content (4502 chars) |
| M2 `editable` memory | ⚠️ partial | `Mythologies` + `Bourriaud` text; no `CORPUS-02` id |
| M3 `Core-Theory-Map.md` | ✅ | Search returns *«ESCLUSO dal corpus attivo»* + Mythologies NOTA |
| M3 `Bibliography-Master.md` | ✅ | § B esclusioni (Mythologies, Bourriaud) |
| M3 `Barthes_Mythologies.md` OCR | ✅ (contradictory) | Ranked **first** on exclusion queries — noise |

**Conclusion:** Not a promotion gap. Content exists; Applicability depends on surfacing path.

### 2. M2 `decisions` not in chat prompt (Infrastructure)

```7:10:backend/app/schemas/memory.py
PROMPT_CONTEXT_KINDS = frozenset({"editable", "user", "thesis"})
```

```1:6:backend/app/graph/memory_context.py
Loads editable + pinned user/thesis from MemoryService
```

`decisions` memory is **stored** but **never injected** into chat turns. CORPUS bindings
are not guaranteed in the system prefix — only whatever overlaps in `editable` (40k chars).

### 3. Grounding instruction conflict (Root cause)

```16:19:backend/app/graph/prompt_wire.py
"Answer the user's question using the numbered sources below..."
"If the sources do not contain the answer, say so explicitly rather than relying on outside knowledge."
```

C.3-R2 agent output (verbatim pattern):

> *«Sulla base dei documenti forniti (fonti [1]–[10]), **non è possibile indicare** quali autori o opere siano stati esplicitamente esclusi»*

The model **followed grounding rules** and scoped answers to `[1]–[10]` retrieved chunks,
**ignoring** the editable/system memory block that C.3-R1 used (*«regole di progetto memorizzate»*).

### 4. Ranking gap — OR-3 prompt retrieval

Simulated `/search` with canonical OR-3 prompt (limit 10):

| Rank | Document | Exclusion content? |
|------|----------|-------------------|
| 1–7 | Outline, Guida, Benjamin OCR, Stigmata | ❌ |
| 8 | Core-Theory-Map | support authors — **not** exclusion section |
| 9–10 | Relatrice PDF, Benjamin | ❌ |

**Zero** top-10 chunks contain `escluso` / CORPUS for the OR-3 query.

Dedicated query `esclusi Mythologies Bourriaud` **does** retrieve Theory Map exclusion
sections — but default retriever uses user message only, one query, limit 10.

### 5. C.3-R1 vs C.3-R2 behavioral diff

| Run | Exclusions | Mechanism (inferred) |
|-----|------------|----------------------|
| **C.3-R1** | ✅ Mythologies + Bourriaud | *«regole di progetto memorizzate»* — editable/system prefix |
| **C.3-R2** | ❌ denied | Scoped to `[1]–[10]` only — grounding instruction |

Same prompt, same runtime (post-EWO-3). Regression is **not** from missing masters; it is
from **interaction between grounding policy and memory prefix** under changed retrieval mix
(more Theory Map author chunks, no exclusion chunks in top-10).

---

## Answer to investigation question

> **Perché il runtime non ha utilizzato CORPUS-02/03 pur essendo disponibili?**

1. **CORPUS decisions are not in the chat prompt path** (`decisions` kind excluded from M2 load).  
2. **Grounding prompt instructs the model to deny** answers not in numbered sources — exclusions are not in top-10 retrieval for the OR-3 query.  
3. **C.3-R1** applied exclusions via editable/system rules; **C.3-R2** did not merge that layer — **model variance** under conflicting instructions.  
4. **Ranking** does not surface exclusion sections for the corpus-listing query without a dedicated retrieval strategy.

---

## Recommended Outer Loop paths (no action taken)

| If classified as… | Recommended WO | EWO category |
|-------------------|----------------|--------------|
| ~~Promotion Gap~~ | ~~Alignment~~ | — ruled out |
| **Grounding Gap** | Patch `prompt_wire` hierarchy (decisions > grounding); or include `decisions` in PROMPT_CONTEXT | **Infrastructure / Runtime** |
| **Ranking Gap** | OR-3 retrieval profile (second query / metadata filter for exclusions) | **Runtime** |
| **Model Variance only** | Robustness protocol (multi-run QWO, statistical PASS) | Process — no immediate EWO |

**Operator recommendation:** single **EWO Runtime/Infrastructure** proposal combining:
- Load M2 `decisions` (or CORPUS slice) into prompt context for chat  
- Revise grounding instruction when system memory contains binding decisions  
- Optional: exclusion-aware retrieval for corpus QWO prompts  

**Not recommended:** EWO-4 Alignment (document promotion) — documents already promoted.

---

## Investigation discipline

| Constraint | Status |
|------------|--------|
| No runtime mutations | ✅ |
| No knowledge mutations | ✅ |
| No memory mutations | ✅ |
| No QWO re-run | ✅ |
| No EWO spawned | ✅ |

---

## WO-TRACE

```text
C.3-R2 FAIL
  → Operator: INVESTIGATE
  → This report
  → (pending) Outer Loop: EWO proposal selection
```

**Supervisor:** may exit WAIT for *investigation complete*; FAIL disposition remains
open until remediation QWO passes or operator accepts alternate path.

---

## Artifacts

| Path | Role |
|------|------|
| `.asep/reports/C.3-R2-investigation.md` | This report |
| `.asep/reports/C.3-R2.md` | QWO FAIL evidence |
| `.asep/reports/stop-20260630-c3-r2-fail.md` | Session STOP |
