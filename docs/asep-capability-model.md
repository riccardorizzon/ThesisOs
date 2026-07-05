# ASEP Capability Model — Knowledge, Coverage, Constraints

> **Binding:** `docs/engineering-program.md`  
> **Gate:** META-1 — **FROZEN** (2026-07-04). Required before C.4 / OR-4; no changes without future META gate.  
> **Scope:** program-agnostic — ThesisOS is one instance

---

## 1. Knowledge domains (not all Ground Truth is the same)

Ground Truth in ASEP is any **frozen authoritative artifact**. Domain type determines
QWO design, FAIL taxonomy, and EWO category — not the file format.

| Domain | Meaning | ThesisOS instance | Typical EWO |
|--------|---------|-------------------|-------------|
| **Scientific** | Disciplinary corpus, theory maps, bibliography | OR-3 masters, books OCR | Alignment, Grounding |
| **Normative** | Rules, policies, institutional constraints | `University-Rules.md`, `Relatrice-Rules.md` | Alignment (promotion) |
| **Procedural** | How to execute a process | STIGMATA framework, revision workflow | Alignment |
| **Organizational** | Project decisions, scope, roles | `Decisions.md`, TODO | Alignment / Governance |

**Rule:** do not qualify normative knowledge with the same contract as scientific corpus.
OR-3 tests **Knowledge Utilization** on scientific GT; OR-4 tests **Constraint Compliance**
on normative GT.

```text
Knowledge Domain
├── Scientific      ← OR-3 (corpus)
├── Normative       ← OR-4 (uni + relatrice)
├── Procedural      ← OR-2 (STIGMATA)
└── Organizational  ← OR-5 (decisions)
```

University and relatrice rules are **Normative Knowledge**, not extensions of the
bibliographic corpus (Eco, Flügel, …).

---

## 2. Knowledge Utilization — decompose broad QWO capabilities

A single QWO (e.g. OR-3) may touch multiple pipeline stages. For audit and re-QWO
discipline, map qualification to **sub-capabilities** without splitting the graph
until a program explicitly refactors nodes.

### C.3 / OR-3 — Knowledge Utilization (retroactive mapping)

| Sub-capability | Pipeline stage | Qualified by | Evidence |
|----------------|----------------|--------------|----------|
| **C.3.1 Retrieval** | Ground Truth → Retrieval | EWO-4A + C.3-R4 | Bibliography-Master in merged context |
| **C.3.2 Grounding** | Retrieval → Grounding | EWO-4 + C.3-R3/R4 | CORPUS-02/03 via `[BINDING DECISIONS]` |
| **C.3.3 Reasoning** | Grounding → Reasoning | C.3-R4 PASS | 12/12 autori, A.1/A.2/A.3 taxonomy |
| **C.3.4 Attribution** | Reasoning → Response | C.3-R4 (partial) | Inline `[n]` cites; some opere «non specificata» |

**Lifecycle rule:** parent `or-3-corpus` → `qualified` only when **all sub-capabilities
required by the Qualification Contract** pass on the latest run. A future Reasoning-only
regression reopens **C.3.3**, not Retrieval — avoids full OR-3 re-qualification when the
failure class is localized.

**Target (future graph):** optional child nodes `or-3-1-retrieval` … `or-3-4-attribution`.
Migration track keeps composite `or-3-corpus` until META refactor.

---

## 3. Traceability Coverage (5th dimension)

Complements the four Coverage dimensions in `docs/engineering-program.md`. Measures
**chain integrity** from response back to Ground Truth — not whether GT exists or
was retrieved, but whether the **answer is anchored**.

```text
Response → Reasoning step → Retrieved evidence → Ground Truth → Corpus
```

| Dimension | Question |
|-----------|----------|
| Ground Truth Coverage | Does GT exist? |
| Runtime Coverage | Is GT promoted and searchable? |
| Qualification Coverage | Did QWO PASS? |
| Evidence Coverage | Is the audit trail complete? |
| **Traceability Coverage** | Can each claim be mapped to a source step? |

**Example:** GT 100%, Qualification PASS, Traceability 71% → synthesis cites wrong
chunk or orphan claim — **Reasoning / Attribution** gap, not Promotion.

**Measurement (QWO reports):** optional score 0–100% from contract checklist:

- % of factual claims with valid `[n]` or binding-decision anchor
- % of listed entities traceable to a named GT artifact section
- orphan claims (no source) counted as failures

Record on capability graph as `coverage.traceability` when assessed.

**OR-3 C.3-R4 (indicative):** high traceability — structured A.1/A.2/A.3, CORPUS anchors,
numerous `[n]` cites; residual gap on support-author **opera titles** (Attribution sub-cap).

---

## 4. Constraint Compliance — OR-4 model

OR-4 must **not** qualify generic “knows the rules”. It qualifies **Constraint Compliance**
against **Normative** Ground Truth.

| Sub-capability | Meaning | ThesisOS OR-4 |
|----------------|---------|---------------|
| **C.4.1 Constraint Acquisition** | Runtime has normative GT promoted | UNI-01, REL-01 in M2/M3 |
| **C.4.2 Constraint Interpretation** | Agent distinguishes institutional vs project preference | guida Accademia vs note minimizzate |
| **C.4.3 Constraint Enforcement** | Agent applies rules when asked / when writing | no forbidden sections, citation style |
| **C.4.4 Constraint Conflict Resolution** | When rules conflict, cites precedence | Constitution > UNI > REL > editable |

QWO sensitivity: **Deterministic** (stable when normative GT is aligned).

**EWO pattern:** **EWO-5A** Alignment (promote normative docs) · **EWO-5B** Constraint Acquisition
(prompt/retrieval path for normative layers). **Grounding** is OR-3 only — not OR-4 remediation.

---

## 4B. Decision Lifecycle Integrity — OR-5 model (C.5 gate)

OR-5 must **not** reduce to “lists open vs closed strings”. It qualifies **Decision Lifecycle
Integrity** on **Organizational** Ground Truth — a **Decision Object**, not a fact.

### Decision Object (ASEP framework entity)

```text
Decision Object
├── id, domain, owner, state
├── created_by, supersedes, superseded_by
├── rationale, evidence
└── effective_from, effective_until
```

Lifecycle: `Draft → Approved → Frozen → Deprecated → Removed`

ThesisOS maps **Congelato** ≈ Frozen; **Da decidere** ≈ open/Draft.

| Sub-capability | Meaning | ThesisOS OR-5 |
|----------------|---------|---------------|
| **C.5.1 Decision Acquisition** | Organizational GT in runtime | `Decisions.md` → M2 `decisions` |
| **C.5.2 Lifecycle State Recognition** | Correct Frozen vs open labels | Congelato vs § Da decidere |
| **C.5.3 Closure Integrity** | Frozen set + open backlog accurate | CORPUS/REV phases + open items |
| **C.5.4 Decision Consistency** | No decision used in lifecycle-incompatible state | Frozen cited as open; inconsistent recommendations |

**Capability vs governance policy:** «Non riproporre senza trigger» is a **governance policy** —
a consequence of Frozen decisions — tested via **C.5.4 Decision Consistency**, not as a
sub-capability named after the policy.

**EWO pattern:** **EWO-6A** Alignment · **EWO-6B** Decision Acquisition — not Grounding.

Proposal: `.asep/proposals/C.5-or-5-decision-lifecycle.md`

### Artifact Issue taxonomy (parallel — not FAIL taxonomy)

Orthogonal to capability FAIL classes. Record in QWO reports; no EWO by default.

```text
Artifact Issue
├── Documentation Defect   (e.g. C.4-R1 REL-03 ID slip)
├── Metadata Defect
└── Formatting Defect
```

Precedent: C.4-R1 REL-03 → Documentation Defect under **Artifact Issue**, not Normative FAIL.

---

## 4C. Academic Artifact Production — OR-6 model (C.6 gate)

OR-6 qualifies **production of a bounded academic artifact** under **already-qualified**
invariants — it does **not** re-run OR-3/4/5 as primary scope.

### Qualified invariants (assumed)

| Gate | Assumed in OR-6 |
|------|-----------------|
| OR-3 | Corpus boundaries in prose |
| OR-4 | Norms embedded in artifact |
| OR-5 | Decision consistency; no unilateral unfreeze |

Violations → **Invariant Regression** (flagged separately from **Writing FAIL**).

| Sub-capability | Meaning | ThesisOS OR-6 |
|----------------|---------|---------------|
| **C.6.1 Production Mode** | Academic register; persona OFF | No emoji/cheerleader |
| **C.6.2 Source-Constrained Synthesis** | **Use** of OR-3-qualified corpus in prose — not re-qualification | Albers §3.2 paragraph |
| **C.6.3 Normative Conformance in Prose** | autore-date; no footnotes in text | OR-4 applied in artifact |
| **C.6.4 Probative Labeling** | Status + FONDATO/PLAUSIBILE | bozza / PRONTO PER REVISIONE |

**EWO pattern:** **EWO-7A** Alignment (procedural docs) · **EWO-7B** Production Path ·
**EWO-7C** Inference Enforcement — not Grounding unless investigation proves
retrieval-only gap in writing turn.

Proposal: `.asep/proposals/C.6-or-6-academic-production.md`

**QWO sensitivity:** Reasoning-sensitive.

### 4D. Model compliance — fifth qualification layer (EWO-7C)

ThesisOS qualification spans five layers beyond raw knowledge:

| Layer | OR gate | What ThesisOS guarantees |
|-------|---------|--------------------------|
| Knowledge correctness | OR-3 | Corpus promoted, retrievable, grounded |
| Policy correctness | OR-4 | Normative rules in runtime |
| Organizational correctness | OR-5 | Decision lifecycle integrity |
| Execution / production | OR-6 | Academic artifact under constraint |
| **Model compliance** | OR-6 (W-06) | **Induce** author-date in output — not deterministic |

**Responsibility boundary (binding — C.6-R3 2026-07-01):**

> **ThesisOS guarantees the maximum documented level of inference enforcement; it does not guarantee deterministic behavior of the underlying LLM.**

When EWO-7B (production path) and EWO-7C (inference enforcement) are both verified and W-06
still fails on live output, the failure class is **Model Non-Compliance** — not OR-6 mis-design,
not OR-4 regression, not production-path defect. Further prompt-only EWO on the same axis
requires **new technical evidence** or an **architectural decision** (accept variance, change
model, add post-generation validation).

**Distinction (binding):**

- **Production path (EWO-7B):** runtime sends the correct instruction.
- **Inference enforcement (EWO-7C):** few-shot, de-priming, output constraints, deterministic single retry when
  `[n]` appears without author-date — still **no post-hoc citation rewriting**.
- **Model limit:** if enforcement exhausts and W-06 still fails, the failure class is
  **model non-compliance**, not OR-6 capability mis-design.

**Evidence:** C.6-R3 — 11/12 oracle; EWO-7C path verified; W-06 FAIL with residual `[2]`.
Report: `.asep/reports/C.6-R3.md`

Implementation: `backend/app/graph/academic_production.py` +
`backend/app/graph/inference_enforcement.py`.

Report: `.asep/reports/EWO-7C-inference-enforcement.md`

### 4F. Memory Runtime Integrity — OR-7 model (C.7 gate)

OR-7 qualifies **persistent project-state management** under qualified invariants — it does
**not** re-run OR-3/4/5/6.

| Sub-capability | Meaning | ThesisOS OR-7 |
|----------------|---------|---------------|
| **C.7.1 State Update Integrity** | Bounded Thesis-State delta | §3.2 bozza pronta per revisione |
| **C.7.2 Change Log Integrity** | Changelog row complete | `YYYY-MM-DD \| file \| azione \| sintesi` |
| **C.7.3 Memory Proposal Discipline** | MEMORY UPDATE as proposal only | No auto-write to permanent |
| **C.7.4 Source Manifest Integrity** | Bibliography candidata coherent | Not promoted to attivi |
| **C.7.5 Decision Lifecycle Preservation** | No Frozen mutation | Masters/decisions read-only |
| **C.7.6 Session Traceability** | Full change chain | Source + rationale per delta |
| **C.7.7 State Atomicity** | Cross-artifact bundle coherence | No partial persistent-state proposal |

**State Atomicity (binding):** MEMORY UPDATE + Thesis-State + Changelog + manifest must form
a coherent closure bundle — see proposal §1.1b, oracle M-09.

**Distinction (binding):**

```text
Capability Failure          Platform Limitation (OR-6 only)
ThesisOS memory path wrong  LLM ignores citation instruction
```

OR-7 is **Deterministic** — failures are Capability Failure (MF-*) unless classified as
Invariant Regression.

**EWO pattern:** **EWO-8A** Alignment · **EWO-8B** Memory Path — not Grounding unless
investigation proves retrieval-only gap in closure turn.

Proposal: `.asep/proposals/C.7-or-7-memory-runtime-integrity.md`

---

### 4E. Capability Failure vs Platform Limitation (PASS*)

QWO oracle checks mix **framework obligations** with **model-dependent outcomes**.
When the evidence chain proves ThesisOS applied all documented controls and a residual
oracle item still fails, classify separately:

```text
Capability Failure          Platform Limitation
──────────────────          ───────────────────
ThesisOS wrong              ThesisOS correct; LLM non-deterministic

Examples:                   Examples:
· wrong corpus              · W-06 autore-date after EWO-7B+7C verified
· wrong routing             · instruction-following gap on probabilistic output
· wrong prompt
· wrong policy / writer
```

**QWO verdict extension (binding):**

| Verdict | Meaning | Lifecycle |
|---------|---------|-----------|
| **PASS** | All oracle items satisfied | → `qualified` |
| **PASS\*** | Capability satisfied; **residual platform limitation documented** | → `qualified` + `platform_limitation` registry |
| **PARTIAL** | Capability gap; remediation or disposition pending | → unchanged unless operator accepts |
| **FAIL** | Capability or invariant failure | → unchanged; EWO / investigate |

**PASS\* requirements (all mandatory):**

1. Complete evidence chain: routing, prompt, enforcement, retry path verified on live run.
2. Residual FAIL items classified as **Platform Limitation**, not Capability Failure.
3. Operator disposition document (`.asep/reports/C.n-Rk-disposition.md`).
4. Mitigation recorded (model replacement \| validation layer \| accept variance).

**Precedent:** OR-6 C.6-R3 — PASS\* with W-06 platform limitation.
Disposition: `.asep/reports/C.6-R3-disposition.md`  
Release artifact: `docs/KNOWN_LIMITATIONS.md`

**Distinction from PARTIAL:**

- **PARTIAL** = ThesisOS may still owe remediation (EWO) or operator has not ruled.
- **PASS\*** = ThesisOS obligation fulfilled; residual gap is **external** to capability design.

---

## 5. Normative FAIL (extends FAIL taxonomy)

Add to Outer Loop routing (`docs/engineering-program.md`):

```text
├── Normative
│     system knows domain but violates operational rule / policy / style constraint
│     → Alignment EWO (missing rule in runtime) OR Constraint Enforcement tweak
│     → NOT Grounding / NOT Reasoning / NOT Structural promotion of corpus
```

| Example | Class |
|---------|-------|
| Uses footnotes when relatrice forbids | **Normative FAIL** |
| Invents relatrice rule from unvalidated transcription | **Normative FAIL** + Governance |
| Mis-lists author as fondamentale | Reasoning / Knowledge Utilization |
| Mythologies in active corpus | Grounding / Applicability |

ThesisOS: OR-4, OR-6 (writing under rules), E2E revision steps — primary Normative FAIL surfaces.

---

## 6. Re-QWO discipline (unchanged, reinforced)

```text
QWO fail → classify (Structural | Grounding | Reasoning | Normative | Governance)
        → EWO targeting cause class
        → re-QWO
```

Never re-QWO without remediation when failure class is **Retrieval-sensitive** (OR-3)
or **Normative** (missing promoted rule).

Canonical OR-3 trace: C.3-R3 REJECT → EWO-4A → C.3-R4 PASS.

---

## 7. META-1 gate before C.4

| Prerequisite | Status |
|--------------|--------|
| OR-3 `qualified` with WO-TRACE intact | ✅ |
| This document published | ✅ |
| `docs/engineering-program.md` cross-links updated | ✅ |
| C.4 proposal uses Constraint Compliance + Normative domain | ✅ approved 2026-06-30 |

Do **not** open C.4 QWO until C.4 proposal explicitly references this model.
