# ThesisOS — Known Limitations (v1.0 Operational)

> **Binding release artifact.** Part of the E.1 baseline freeze (2026-07-01).  
> Changes after baseline require a new engineering change process — not silent edits.

This document defines what **ThesisOS guarantees** versus what depends on the
**underlying LLM** or **operational assumptions**. It is not a bug list; it is
the formal boundary of the qualified framework.

---

## 1. Framework vs model

| Layer | ThesisOS responsibility | Not ThesisOS responsibility |
|-------|-------------------------|------------------------------|
| Knowledge | Corpus promoted, retrievable, grounded (OR-3) | — |
| Governance | Normative rules in runtime (OR-4) | — |
| Decisions | Lifecycle integrity (OR-5) | — |
| Production | Academic artifact under constraint (OR-6) | Deterministic author-date on every generation |
| Memory | Session closure, proposals, state atomicity (OR-7) | — |
| Integration | OR-1…OR-7 cooperate in continuous session (E2E) | — |
| **Model** | Maximum documented inference enforcement (EWO-7B/7C) | Instruction-following variance |

**Binding principle** (C.6-R3 disposition, `docs/asep-capability-model.md` §4E):

> ThesisOS guarantees the maximum documented level of inference enforcement; it
> does not guarantee deterministic behavior of the underlying LLM.

**Capability Failure ≠ Platform Limitation**

- **Capability Failure** — ThesisOS wrong (routing, prompt, memory path, corpus, policy).
- **Platform Limitation** — ThesisOS correct; residual gap is probabilistic model behavior.

---

## 2. W-06 — Platform Limitation (autore-date citations)

### Description

Oracle criterion **W-06** requires inline **author-date** citations
`(Author, YYYY)` in academic prose — not numeric bracket cites `[1], [2]`.

After full ThesisOS enforcement (production path + inference enforcement + single
deterministic retry), the live model may still emit numeric citations in some runs.

### Evidence chain

| Run | Enforcement | W-06 | Classification |
|-----|-------------|------|----------------|
| C.6-R1 | pre-EWO-7B | FAIL `[2]` | Capability Failure → EWO-7B |
| C.6-R2 | EWO-7B verified | FAIL `[2]` | Model non-compliance suspected |
| C.6-R3 | EWO-7B + EWO-7C verified | FAIL residual `[2]` | **Platform Limitation** |

Reports: `.asep/reports/C.6-R1.md`, `C.6-R2.md`, `C.6-R3.md`  
Disposition: `.asep/reports/C.6-R3-disposition.md` (PASS\*)

### OR-6 qualification

OR-6 is **`qualified` with PASS\*** — capability obligation fulfilled; W-06
recorded as external platform limitation, not OR-6 design defect.

Capability graph: `or-6-write-paragraph.platform_limitation.oracle_id: W-06`

### Mitigations (architectural — not in v1.0 baseline)

1. **Model replacement** — re-run C.6-R3 under a different LLM.
2. **Post-generation validation layer** — reject/rewrite output missing author-date
   (outside current OR-6 oracle contract).
3. **Accept variance** — operator revision workflow handles residual numeric cites.

### PX-6 partial mitigation (2026-07-07)

**Status:** **PARTIALLY MITIGATED** via product validation layer (PX6-EWO-002…004).

| Layer | Delivered |
|-------|-----------|
| Detection | Deterministic flag of numeric `[n]` in Writing editor and AI proposals |
| Suggestion | Author-date hint from source metadata when available |
| Gating | Optional block on AI **Applica** until override |
| API | `POST /citations/validate` |

**Still not guaranteed:** deterministic author-date on every LLM generation. OR-6
remains **PASS\***; W-06 is mitigated in product UX, not eliminated at model layer.

Evidence: `.asep/reports/PX6-INTEGRATION-A.md`, `docs/product/specs/px6-polish-experience-v1.md` §4.

### What ThesisOS still guarantees for writing

- Academic register; persona OFF (OR-6 C.6.1)
- Source-constrained synthesis; A/B separation (C.6.2)
- Probative labeling; status labels (C.6.4)
- Inference enforcement stack deployed and verified on live path

---

## 3. E2E observation

E2E-1 (D.1) may use numeric `[n]` in library-first analysis — consistent with W-06.
E2E **PASS** evaluates integration cooperation, not re-proof of autore-date determinism.

Report: `.asep/reports/D.1-E2E.md`

---

## 4. Operational assumptions

ThesisOS v1.0 Operational assumes:

| Assumption | Basis |
|------------|-------|
| **Promoted corpus** | Phase B + EWO-3/4/4A; OR-3 qualified |
| **Frozen decisions** | Decisions.md + M2 `decisions`; OR-5 qualified |
| **Normative GT** | University + relatrice rules promoted; OR-4 qualified |
| **Live stack** | Docker compose backend + DB; `/health` OK |
| **No silent GT mutation** | QWO/E2E do not modify Ground Truth without operator approval |
| **Memory writes** | MEMORY UPDATE PROPOSAL only until operator approves |
| **Operator gate** | Frozen masters (Outline, Bibliography-Master, Theory Map) not unilaterally edited |

If these assumptions are violated in deployment, qualification evidence does not apply.

---

## 5. Post-baseline change policy

After E.1 freeze:

- No capability, oracle, acceptance criteria, or governance changes without a
  **new engineering change process** (WorkOrder + report + operator authorization).
- W-06 mitigation via new EWO requires **architectural decision** — not prompt-only iteration.

---

## WO-TRACE

```text
C.6-R3 PASS* → W-06 Platform Limitation → E.1 KNOWN_LIMITATIONS.md → v1.0 Operational
```
