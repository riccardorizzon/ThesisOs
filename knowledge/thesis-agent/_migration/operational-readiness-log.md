# Operational Readiness — log esecuzioni

Registro esiti dei test OR-1 … OR-7 (`operational-readiness.md`).

## Stato sintesi (2026-07-01) — **FROZEN @ E.1**

| OR | Ultimo run | Esito live | Capability lifecycle |
|----|------------|------------|----------------------|
| OR-1 | C.1-R2 | **PASS** | `qualified` |
| OR-2 | C.2-R2 | **PASS** | `qualified` |
| OR-3 | C.3-R4 | **PASS** | `qualified` |
| OR-4 | C.4-R1 | **PASS** | `qualified` |
| OR-5 | C.5-R1 | **PASS** | `qualified` |
| OR-6 | C.6-R3 | **PASS\*** | `qualified` — W-06 Platform Limitation |
| OR-7 | C.7-R1 | **PASS** | `qualified` |
| E2E | e2e-2026-07-01 | **PASS** | `frozen` |
| **Release** | E.1 | **COMPLETE** | `thesisos-v1.0-operational` |

**ThesisOS v1.0 Operational** — migration program complete.  
Manifest: `docs/RELEASE-MANIFEST-v1.0.yaml` · Limitations: `docs/KNOWN_LIMITATIONS.md`

---

## Registro esecuzioni (cronologico inverso)

| Data | Run | Agente | OR-1 | OR-2 | OR-3 | OR-4 | OR-5 | OR-6 | OR-7 | Verdetto |
|------|-----|--------|------|------|------|------|------|------|------|----------|
| 2026-07-01 | **E.1** Release Baseline | v1.0 Operational freeze | — | — | — | — | — | — | — | **RELEASE COMPLETE** |
| 2026-07-01 | **D.1 E2E** | continuous session · conv `9e6762fb…` | — | — | — | — | — | — | — | **E2E PASS** |
| 2026-07-01 | **C.6-R3** QWO | live `/chat` · conv `27d1b8c2…` | — | — | — | — | — | **PASS\*** | — | **OR-6 PASS\*** (W-06 platform limitation) |
| 2026-07-01 | **EWO-7C** | inference enforcement layer | — | — | — | — | — | — | — | audit PASS |
| 2026-07-01 | **C.6-R2** QWO | live `/chat` · conv `8290ba23…` | — | — | — | — | — | **PARTIAL** | — | **OR-6 PARTIAL** (W-06 model) |
| 2026-07-01 | **EWO-7B** | academic production path | — | — | — | — | — | — | — | audit PASS |
| 2026-06-30 | **C.6-R1** QWO | live `/chat` · conv `f28c9067…` | — | — | — | — | — | **PARTIAL** | — | **OR-6 PARTIAL** |
| 2026-06-30 | **C.5-R1** QWO | live `/chat` · conv `ed9226af…` | — | — | — | — | **PASS** | — | — | **OR-5 PASS** |
| 2026-06-30 | **C.4-R1** QWO | live `/chat` · conv `6e7489ac…` | — | — | — | **PASS** | — | — | — | **OR-4 PASS** |
| 2026-06-30 | **C.3-R4** QWO | live `/chat` · conv `818d5c0e…` | — | — | **PASS** | — | — | — | — | **OR-3 PASS** |
| 2026-06-30 | **EWO-4A** | corpus-list grounding | — | — | — | — | — | — | — | audit PASS |
| 2026-06-30 | **C.3-R3** QWO | live `/chat` · conv `6867c597…` | — | — | **PARTIAL** | — | — | — | — | **REJECTED** |
| 2026-06-30 | **C.3-R2** QWO | live `/chat` · conv `fcc5b450…` | — | — | **FAIL** | — | — | — | — | **OR-3 FAIL** |
| 2026-06-30 | **C.3-R1** QWO | live `/chat` · conv `478cbcd5…` | — | — | **PARTIAL** | — | — | — | — | **OR-3 PARTIAL** |
| 2026-06-30 | **C.2-R2** QWO | live `/chat` · conv `3c1ba5a4…` | — | **PASS** | — | — | — | — | — | **OR-2 PASS** |
| 2026-06-30 | C.2-R1 QWO | live `/chat` · conv `e4b0c047…` | — | **PARTIAL** | — | — | — | — | — | **OR-2 PARTIAL** |
| 2026-06-30 | **C.1-R2** QWO | live `/chat` · conv `d6673e25…` | **PASS** | — | — | — | — | — | — | **OR-1 PASS** |
| 2026-06-30 | C.1-R1 QWO | live `/chat` · conv `f1700ff2…` | **FAIL** | — | — | — | — | — | — | **OR-1 FAIL** |
| 2026-06-30 | baseline | markdown-only (audit agente) | PASS | PASS | PASS | PARTIAL | PASS | PARTIAL | PARTIAL | superato da QWO live |

### E2E (End-to-End Project Test)

| Run | Scenario | E2E-1..6 | G1..G5 | Verdetto | Osservatore |
|-----|----------|----------|--------|----------|-------------|
| **e2e-2026-07-01** | Albers → §3.2 · conv `9e6762fb…` | **PASS** | **PASS** | **E2E PASS** | agent runner (no hidden intervention) |

---

### Note E.1 Release Baseline 2026-07-01

- **ThesisOS v1.0 Operational** — E.1 COMPLETE.
- Frozen: manifest, capability registry, operational log, KNOWN_LIMITATIONS.
- Report: `.asep/reports/E.1-release-baseline.md` · QC: `.asep/certificates/E.1-20260701.yaml`
- Tag recommended: `thesisos-v1.0-operational` (at baseline commit).

### Note D.1 E2E 2026-07-01

- **E2E PASS.** 6-step continuous session; E2E-1…E2E-6 + G1…G5 PASS.
- Principle: **No Hidden Operator Intervention** — single `conversation_id`, no mid-session state injection.
- W-06 numeric cites in E2E-1 — Platform Limitation (non integration defect).
- Report: `.asep/reports/D.1-E2E.md` · QC: `.asep/certificates/D.1-E2E-20260701.yaml`
- `e2e-session` → **`operational`**. Migration integration gate satisfied → **E.1** pending.

### Note C.7-R1 QWO 2026-07-01

- **OR-7 PASS.** Session closure: MEMORY UPDATE + Itten candidata + §3.2 Thesis-State + Changelog + manifest coherence.
- Oracle **9/9** (M-01…M-09); State Atomicity preserved; no IR.
- Report: `.asep/reports/C.7-R1.md` · QC: `.asep/certificates/C.7-R1-20260701.yaml`
- `or-7-memory-update` → **`qualified`**. E2E unblocked.

### Note C.7 approval + pre-flight 2026-07-01

- **C.7 APPROVED** — OR-7 Memory Runtime Integrity; oracle M-01…M-09 (+ State Atomicity).
- Pre-flight: **85%** Runtime Coverage — `.asep/reports/C.7-preflight-runtime-audit.md`
- `or-7-memory-update` → **`approved`**. C.7-R1 requires separate authorization.

### Note C.6-R3 disposition 2026-07-01 (operator PASS*)

- **C.6-R3 ACCEPTED as PASS\*** — OR-6 Capability Qualified with External Platform Limitation.
- Distinzione: **Capability Failure ≠ Platform Limitation** (`docs/asep-capability-model.md` §4E).
- W-06 → Known Platform Limitation; mitigation: model replacement | validation layer.
- `or-6-write-paragraph` → **`qualified`**. OR-7 unblocked.
- Disposition: `.asep/reports/C.6-R3-disposition.md`

### Note C.6-R3 QWO 2026-07-01 (post-EWO-7C — final requalification)

- **OR-6 PASS\*** (operator disposition). Oracle 11/12; W-06 = Platform Limitation.
- **EWO-7C path verified:** de-priming, few-shot, inference enforcement, retry guard wired.
- Report: `.asep/reports/C.6-R3.md` · QC: `.asep/certificates/C.6-R3-20260701.yaml`
- **No further EWO** on W-06 without architectural decision.

### Note EWO-7C 2026-07-01

- **Inference Enforcement Layer** implemented — few-shot, de-priming, output constraints, single retry guard.
- Model compliance layer documented (`docs/asep-capability-model.md` §4D).
- Report: `.asep/reports/EWO-7C-inference-enforcement.md`
- Next: backend restart → **C.6-R3**.

### Note C.6-R2 QWO 2026-07-01 (post-EWO-7B)

- **OR-6 PARTIAL.** Same W-06 gap: `[2]` ×3, no `(Albers, 1963)`.
- **Prompt path verified:** author-date instruction live; numeric instruction absent.
- **Classification:** model non-compliance — not stale production path.
- Report: `.asep/reports/C.6-R2.md` · QC: `.asep/certificates/C.6-R2-20260701.yaml`
- Recommended: **EWO-7C** (citation enforcement) → **C.6-R3**.

### Note operator disposition C.6-R1 → EWO-7B (2026-07-01)

- **C.6-R1 PARTIAL: REJECTED** — W-06 systemic production-path failure (not content variance).
- **EWO-7B APPROVED** — author-date citation discipline in `academic_production.py` + prompt wire.
- Report: `.asep/reports/EWO-7B-academic-production-path.md`
- Next: restart backend → **C.6-R2** QWO.

### Note C.6-R1 QWO 2026-06-30

- **OR-6 PARTIAL.** Paragraph §3.2 Albers produced; A/B + FONDATO/PLAUSIBILE + persona OFF + status OK.
- **Gap:** W-06 autore-data — numeric `[2]` instead of `(Albers, YYYY)` → C.6.3 FAIL.
- **No Invariant Regression;** traceability 100%.
- Report: `.asep/reports/C.6-R1.md` · Stop: `.asep/reports/stop-20260630-c6-r1-partial.md`
- **No system mutations** during QWO.
- Recommended: **EWO-7B** (Production Path) → **C.6-R2**.

### Note C.5-R1 QWO 2026-06-30

- **OR-5 PASS.** Congelata/Aperta lifecycle; CORPUS/REV/METH/RED/UNI decisions; masters frozen; § Da decidere open items; decision consistency (no reopen).
- **Runtime:** pre-flight 80%; M2 `decisions` + `thesis`.
- Report: `.asep/reports/C.5-R1.md` · QC: `.asep/certificates/C.5-R1-20260630.yaml`
- **No system mutations** during QWO.
- Residual: STIGMATA materials as contextual open item (Artifact Issue — non-blocking).
- `or-5-decisions` → **`qualified`**. C.6 / OR-6 unblocked.

### Note C.4-R1 QWO 2026-06-30

- **OR-4 PASS.** Agent listed UNI-01 institutional rules, REL-01 R1–R5, distinguished layers; footnote ban **vietate** (RED-02); conflict table guida vs project.
- **Runtime:** pre-flight 90%; M2 `university-rules` + `relatrice-rules` + decisions.
- Report: `.asep/reports/C.4-R1.md` · QC: `.asep/certificates/C.4-R1-20260630.yaml`
- **No system mutations** during QWO.
- Residual: REL-03 mis-label in table (non-blocking).
- `or-4-rules` → **`qualified`**. C.5 / OR-5 unblocked.

### Note C.3-R4 QWO 2026-06-30

- **OR-3 PASS.** 12/12 autori; CORPUS-02/03 esclusioni; FOND/SUPPORTO; A.1/A.2/A.3 applicability — post-EWO-4A.
- Report: `.asep/reports/C.3-R4.md`
- **No system mutations** during QWO.
- `or-3-corpus` → **`qualified`**. C.4 unblocked.

### Note C.3-R3 disposition 2026-06-30

- **C.3-R3 PARTIAL: REJECTED** — OR-3 non promosso.
- Grounding/esclusioni OK; gap residuo: Eco/Flügel + FOND/SUPPORTO.
- Next: **C.3-R4** — `.asep/reports/C.3-R3-disposition.md`

### Note C.3-R3 QWO 2026-06-30 (post-EWO-4 Grounding)

- **OR-3 PARTIAL** — disposition **pending** operator (Level 2 STOP).
- **Applicability restored:** CORPUS-02/03 + `[BINDING DECISIONS]` in output (vs C.3-R2 regression).
- **Completeness gap:** 10/12 autori (Eco, Flügel missing); FOND/SUPPORTO taxonomy imprecise.
- Backend rebuilt/restarted before QWO.
- Report: `.asep/reports/C.3-R3.md` · Stop: `.asep/reports/stop-20260630-c3-r3-partial.md`

### Note operator governance 2026-06-30

- **C.3-R2 Investigation:** ACCEPTED — Primary **Grounding Gap**; Secondary Ranking; Tertiary Model Variance; Structural Promotion Gap **REJECTED**.
- **EWO-4 proposal:** APPROVED — category **Grounding** (new EWO class).
- **Cognitive pipeline:** Ground Truth → Retrieval → Grounding → Reasoning → Response (formalized in `docs/engineering-program.md`).
- **Category:** Grounding (new) — prompt pipeline + M2 decisions + exclusion-aware retrieval.
- Investigation ACCEPTED → EWO-4 **implemented**.
- Report: `.asep/reports/EWO-4-runtime-grounding-alignment.md`
- Next: restart backend → **C.3-R3** re-QWO.

### Note C.3-R2 investigation 2026-06-30

- **Disposition:** `C.3-R2 FAIL: INVESTIGATE` (operator).
- **Verdict:** Primary **Grounding Gap** + Ranking Gap; **NOT** Promotion Gap.
- **Evidence:** `prompt_wire.py` grounding rule; M2 `decisions` not in PROMPT_CONTEXT; retrieval sim.
- Report: `.asep/reports/C.3-R2-investigation.md`
- **Remediation:** EWO-4 **Grounding** (operator APPROVED 2026-06-30) — not Alignment/Promotion.

### Note C.3-R2 QWO 2026-06-30 (ASEP continua L2)

- **OR-3 FAIL.** Masters promoted (EWO-3); 8/12 autori in output; **CORPUS-02/03 esclusioni assenti** — Applicability regression vs C.3-R1.
- **Not promotion gap** — Runtime Coverage ~100%.
- Auto-authorized via QC Certificate `.asep/certificates/C.3-R2-20260630.yaml`.
- **Supervisor STOP:** `.asep/reports/stop-20260630-c3-r2-fail.md` (T11 + T2).
- Report: `.asep/reports/C.3-R2.md`
- **No system mutations** during QWO.

### Note C.3-R1 QWO 2026-06-30

- **OR-3 PARTIAL** — **ACCEPTED** Outer Loop 2026-06-30.
- Exclusioni CORPUS-02/03 corrette; Applicability PASS; Completeness insufficient (masters assenti).
- **EWO-3 implemented** — masters promoted; Runtime Coverage ~100%.
- Report: `.asep/reports/C.3-R1.md` · EWO-3: `.asep/reports/EWO-3-runtime-corpus-alignment.md`
- Next: **C.3-R2** re-QWO (separate authorization).

### Note C.2-R2 QWO 2026-06-30

- **OR-2 PASS.** DOCUMENTATION_MASTER taxonomy, evidence levels (FONDATO/PLAUSIBILE/NON VERIFICABILE/APPLICAZIONE TESI), METH-02, cap. 5 link — post-EWO-2.
- Report: `.asep/reports/C.2-R2.md`
- **No system mutations** during QWO.
- `or-2-stigmata-framework` → **`qualified`**. OR-3 unblocked (C.3 proposal next).

### Note C.2-R1 QWO 2026-06-30

- **OR-2 PARTIAL** (valid). METH-02 + cap. 5 link + evidence-first OK; DOCUMENTATION_MASTER, EVIDENCE MATRIX, livelli evidenza **missing**.
- **Cause:** promotion gap — `Stigmata-Framework.md` not in runtime M3/M4.
- Report: `.asep/reports/C.2-R1.md` — **ACCEPTED** PARTIAL
- **No system mutations** during QWO.
- Outer Loop: **EWO-2 spawned** (`.asep/proposals/EWO-2-runtime-methodology-alignment.md`).

### Note C.1-R2 QWO 2026-06-30

- **OR-1 PASS.** Agent reconstructed 6-chapter Ground Truth; domanda GT fedele; macro-fasi teoria / STIGMATA / conclusioni.
- **Runtime:** post-EWO-1 (outline indexed, thesis memory v4).
- Report: `.asep/reports/C.1-R2.md`
- **No system mutations** during QWO.
- `or-1-thesis-structure` → **`qualified`**. OR-2 unblocked (C.2 proposal next).

### Note C.1-R1 QWO 2026-06-30

- **OR-1 FAIL** (valid). Agent collapsed 6-chapter Ground Truth → 3 blocks; cap. 2/3 misassigned; cap. 4–6 missing.
- **Cause:** promotion gap (`Outline-Master` not in runtime) + incomplete `thesis` memory.
- Report: `.asep/reports/C.1-or-1.md` (run id **C.1-R1**)
- **No system mutations** during QWO.
- Next: **EWO-1 proposal** → re-QWO C.1. OR-2 blocked.

### Note baseline 2026-06-30

- Fase A **chiusa:** UNI-01 + REL-01 (R1–R5) congelati.
- Fase B **completata:** memories + 16 documents + 8 chapters promossi (`promotion-log.md`).
- Fase C **in corso:** OR-1…OR-5 PASS live · OR-6 C.6-R1 REJECT → **EWO-7B PASS** · C.6-R2 pending · OR-7 pending · E2E pending.
- Prossima esecuzione: **C.6-R2** (post backend restart).
