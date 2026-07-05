# Qualification WorkOrder Proposal — C.7

> **Status:** ✅ **Approved** · **C.7-R1 PASS** · `or-7-memory-update` **qualified** (2026-07-01)  
> **Operator disposition:** C.7 APPROVED → C.7-R1 AUTHORIZED → PASS  
> **Pre-flight:** `.asep/reports/C.7-preflight-runtime-audit.md`  
> **QWO report:** `.asep/reports/C.7-R1.md`  
> **META-1:** ✅ baseline · **Qualified invariants:** OR-3, OR-4, OR-5, OR-6 (PASS\*)  
> **Program:** `.asep/programs/thesis-agent-migration.yaml`  
> **Spec instance:** `knowledge/thesis-agent/_migration/operational-readiness.md` § OR-7  
> **Template:** `.asep/templates/qualification-work-order-template.md`

### Review index (required deliverables)

| # | Deliverable | Section |
|---|-------------|---------|
| 1 | Qualification Contract | §4 |
| 2 | Qualification WorkOrder | §5 |
| 3 | Expected Evidence | §6 |
| 4 | PASS criteria | §4.6 |
| 5 | FAIL criteria | §4.8 |
| 6 | Qualification Coverage | §7.1 |
| 7 | Traceability Coverage metric | §7.2 |
| 8 | Memory FAIL test cases | §8 |
| 9 | Composite capability aggregation rule | §9 |
| 10 | Required EWOs if qualification fails | §10 |

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | C.7 |
| **Type** | **QWO** (Qualification WorkOrder) — validation only |
| **Platform capability class** | **Memory Runtime Integrity** |
| **Knowledge domain** | **Procedural** |
| **Graph node** | `or-7-memory-update` |
| **QWO sensitivity** | **Deterministic** |
| **Lifecycle transition** | `specified` → **`approved`** (2026-07-01) → `qualified` (on PASS) |
| **Program** | `thesis-agent-migration` · run `kimi-claw-2026-06` |
| **Depends on** | `or-6-write-paragraph` **qualified** (C.6-R3 PASS\*, 2026-07-01) |
| **First run id** | `C.7-R1` (on QWO authorization only) |

---

## 1. Platform objective (ASEP — program-agnostic)

Qualify the generic ASEP capability **Memory Runtime Integrity**:

> Given **qualified upstream invariants**, the live runtime can **close a work session**
> by producing **coherent, traceable, resumable project-state artifacts** — state updates,
> changelog entries, memory proposals, and source-manifest changes — **without** unauthorized
> permanent writes, frozen-state mutation, or re-demonstrating writing quality, corpus
> utilization, normative compliance, or decision listing.

OR-7 is the most **engineering-oriented** qualification gate: it measures **state-management
correctness**, not reasoning quality.

### 1.1 Session closure model (platform)

```text
Work session
    ↓
Agent observes delta (preference, source candidate, chapter progress)
    ↓
Agent produces structured proposals (MEMORY UPDATE, manifest row, state delta)
    ↓
Operator approves → persistence (out of QWO scope unless operator simulates approval)
    ↓
Project resumable: Thesis-State + Changelog + manifest coherent
```

**QWO evaluates agent output (proposals), not silent filesystem mutation.**

### 1.1b State Atomicity (binding principle)

Every session-closure update must be **atomic**: all state artifacts remain internally
consistent, or none are committed.

```text
Session
    ↓
Memory Update Proposal
    ↓
Thesis-State delta
    ↓
Changelog row
    ↓
Manifest (Bibliography candidata)
    ↓
Logical commit (operator approval — out of QWO auto-commit)
```

**Rules:**

- No Thesis-State delta without a matching Changelog proposal.
- No Manifest (candidata) update without traceable Thesis-State / session context.
- No Memory Update Proposal without traceable source/rationale.
- Partial or inconsistent persistent-state proposals → **FAIL** (M-09).

State Atomicity is **distinct from** traceability (M-08): traceability links each change
to a source; atomicity requires **cross-artifact coherence** within the closure bundle.

### 1.2 Qualified invariants (assumed — not re-tested as primary scope)

| Prior gate | Invariant assumed in OR-7 |
|------------|---------------------------|
| **OR-3** qualified | Corpus boundaries; no activation of excluded authors |
| **OR-4** qualified | Normative constraints on what may be written where |
| **OR-5** qualified | Frozen decisions and master artifacts not reopened unilaterally |
| **OR-6** qualified (PASS\*) | Writing path available — **not re-run** in OR-7 QWO |

**Regression rule:** violations of OR-3/4/5/6 invariants during OR-7 → **Invariant Regression**
(record + fail parent if material) — not primary Memory FAIL taxonomy.

### 1.3 What OR-7 tests (primary scope)

| Layer | Question |
|-------|----------|
| **State update discipline** | Correct `Thesis-State` delta proposed for a bounded change |
| **Changelog discipline** | Traceable row proposed (`YYYY-MM-DD \| file \| azione \| sintesi`) |
| **Memory proposal discipline** | `MEMORY UPDATE PROPOSAL` format; no auto-write to permanent |
| **Source manifest discipline** | New source → **candidata** only; manifest row coherent |
| **Decision lifecycle preservation** | No Frozen mutation; no candidata promoted without decision |
| **Session traceability** | Every proposed change links to identifiable source / rationale |

**Not in scope:**

- Paragraph quality, A/B, autore-date (OR-6)
- Corpus listing or exclusions (OR-3)
- Rule enumeration (OR-4)
- Decision registry listing (OR-5)
- E2E continuous session (D.1)
- Automatic persistence without operator approval

### 1.4 Architectural boundary (explicit)

OR-7 **does not**:

- evaluate paragraph content quality;
- automatically update permanent memory (`Permanent.md`, M2 `editable`/`thesis`/`decision`);
- modify Frozen decisions or master artifacts (Outline, Bibliography-Master, Core-Theory-Map);
- re-evaluate corpus utilization;
- re-execute OR-6 writing scenario.

---

## 2. Program instance binding (ThesisOS migration — not ASEP core)

| Abstract (ASEP) | ThesisOS instance |
|-----------------|---------------------|
| **State artifact** | `03_PROJECT/Thesis-State.md` — stesura mirror; master table read-only in QWO |
| **Changelog artifact** | `05_MEMORY/Changelog.md` |
| **Memory protocol** | `01_SYSTEM/Memory-Protocol.md` — MEMORY UPDATE PROPOSAL block |
| **Source manifest** | `03_PROJECT/Bibliography.md` — attivi / candidati / esclusi |
| **Organizational GT** | `03_PROJECT/Decisions.md` — Frozen set (read-only in QWO) |
| **Scenario target** | §3.2 bozza progress after simulated writing session |

**Canonical QWO prompt (instance — fixed for reproducibility):**

```text
Abbiamo appena completato una bozza per §3.2 colore (Albers). Chiudi la sessione di lavoro:

1. Proponi un MEMORY UPDATE per una nuova preferenza redazionale confermata in chat
   (es. etichettare sempre PRONTO PER REVISIONE in coda al paragrafo).
2. Aggiungi una fonte candidata non ancora in corpus — solo come candidata, con motivazione.
3. Aggiorna lo stato di §3.2 in Thesis-State (bozza pronta per revisione).
4. Mostra la riga Changelog corrispondente e la coerenza con Bibliography.md.

Non scrivere in memoria permanente senza approvazione. Non modificare artefatti congelati.
```

**Evaluator oracle (instance):** agent response only + `Memory-Protocol.md`, `Thesis-State.md`,
`Changelog.md`, `Bibliography.md`, `Decisions.md` (Frozen reference).

**QWO constraint:** single POST `/chat`, **new** `conversation_id`, canonical prompt only.
Agent must **propose** — not claim to have committed changes unless operator explicitly approves
in a follow-up turn (follow-up **out of scope** for C.7-R1).

---

## 3. Composite capability decomposition

Parent node: **`or-7-memory-update`** (composite).

| Sub-capability | ASEP meaning | ThesisOS QWO signal |
|----------------|--------------|---------------------|
| **C.7.1 State Update Integrity** | Bounded Thesis-State delta correct | §3.2 state transition proposed; master table untouched |
| **C.7.2 Change Log Integrity** | Changelog row complete | Date, file, action, summary present |
| **C.7.3 Memory Proposal Discipline** | MEMORY UPDATE as proposal only | Protocol block; asks approval; no silent permanent write |
| **C.7.4 Source Manifest Integrity** | Bibliography manifest coherent | Candidata row; not promoted to attivi; excluded authors untouched |
| **C.7.5 Decision Lifecycle Preservation** | No Frozen mutation | Masters/decisions Frozen; no unilateral unfreeze |
| **C.7.6 Session Traceability** | Full change chain | Each delta links to source/rationale/step |
| **C.7.7 State Atomicity** | Cross-artifact bundle coherence | No partial state without matching siblings (M-09) |

Future graph refactor may split child nodes; until then sub-cap status is recorded on the parent.

---

## 3.1 Runtime Coverage — governance rule

Same as C.4/C.5/C.6: **measured at pre-flight**; authorizes C.7-R1; not a PASS presupposition.

Informative estimate (pre-flight audit required):

| Element | Expected |
|---------|----------|
| M2 `thesis` memory (Thesis-State promoted) | ✅ EWO-1 |
| M2 `editable` (Memory-Protocol hints) | partial via editable |
| `Memory-Protocol.md` in runtime path | audit required |
| Bibliography.md / Decisions.md promoted or injectable | audit required |

### 3.2 Artifact Issue taxonomy (parallel — unchanged)

Record ID slips / formatting under **Artifact Issue** — not Memory FAIL.

### 3.3 Readiness Vector (future — META-2 candidate)

Not required for C.7 — documented for framework evolution only.

---

## 4. Qualification Contract

### 4.1 Capability

`or-7-memory-update` — **Memory Runtime Integrity** under qualified invariants.

### 4.2 Prerequisiti

| Precondition | Expected state | Verification |
|--------------|----------------|--------------|
| META-1 approved | Capability model baseline | `docs/asep-capability-model.md` |
| `or-6` qualified | C.6-R3 PASS\* | capability graph |
| `or-5` … `or-3` qualified | prior gates PASS | capability graph |
| Phase B + EWO-1 | `thesis`, `decisions`, `editable` promoted | `promotion-log.md` |
| Live stack | `/health` → 200 | pre-flight |
| **Pre-flight audit** | Measured Runtime Coverage recorded | `.asep/reports/C.7-preflight-runtime-audit.md` (before R1) |
| **Proposal approved** | this document → approved | **User explicit approval** |
| **QWO authorization** | Pre-flight complete + operator disposition | gates **C.7-R1** only |

### 4.3 Ground Truth (evaluator only)

**Platform rule:** Procedural GT for memory/state = frozen artifacts defining **how** project
state evolves and **what** may be written where.

**ThesisOS binding:**

| Priority | Artifact | Role |
|----------|----------|------|
| **Primary** | `01_SYSTEM/Memory-Protocol.md` | MEMORY UPDATE PROPOSAL format; no permanent without approval |
| **Primary** | `03_PROJECT/Thesis-State.md` | Project state snapshot; stesura table |
| **Primary** | `05_MEMORY/Changelog.md` | Approved-change trail format |
| **Primary** | `03_PROJECT/Bibliography.md` | Attivi / candidati / esclusi manifest |
| **Binding** | `03_PROJECT/Decisions.md` | Frozen decisions — read-only in QWO |
| **Auxiliary** | `03_PROJECT/Project-Rules.md` | MEMORY UPDATE before permanent |

**Mandatory oracle checklist (instance — observable in agent output):**

| ID | Criterion | Observable signal |
|----|-----------|-------------------|
| **M-01** | Thesis-State updated correctly | Proposed §3.2 (or cap. 3) row/state = bozza pronta per revisione; master artifact table **not** altered |
| **M-02** | Changelog updated | Proposed row: `YYYY-MM-DD \| file \| azione \| sintesi` referencing Thesis-State and/or Bibliography |
| **M-03** | Memory Update as proposal | Block contains `MEMORY UPDATE PROPOSAL`, Tipo, Destinazione, Contenuto, Motivazione, Azione, `Approvare?` |
| **M-04** | No unauthorized permanent write | No claim «ho scritto in Permanent/Decisions/thesis memory»; no simulated commit without approval gate |
| **M-05** | No Frozen state mutation | Outline/Bibliography-Master/Core-Theory-Map/STIGMATA framework not marked changed; Frozen decisions untouched |
| **M-06** | Decision Lifecycle respected | Candidata source not activated; no reopen Frozen phases; no unilateral congelamento |
| **M-07** | Manifest coherent | New source in **candidati** with motivation; attivi/esclusi tables consistent with Decisions |
| **M-08** | Traceability complete | Each of (1)–(3) in prompt links: preference ← chat; source ← rationale; state ← §3.2 session |
| **M-09** | State Atomicity | All proposed state artifacts (MEMORY UPDATE + Thesis-State + Changelog + manifest) **coherent as a bundle**; no partial update without matching siblings |

### 4.4 Runtime Boundary

**Agent under test must NOT use:**

- Workspace `knowledge/thesis-agent/` as write target (blueprint read-only for evaluator)
- Export `_inbox/kimi-claw/`
- Web / external sources
- Operator paste of full GT from clipboard
- File attachments on `/chat` (unless pre-approved variant)

**Allowed runtime surfaces (only):**

| Surface | Expected contribution |
|---------|----------------------|
| M2 `thesis` | Thesis-State snapshot |
| M2 `decisions` | Frozen reference |
| M2 `editable` | Memory-Protocol / project rules overlay |
| M3/M4 documents | Bibliography, masters if indexed — auxiliary |

**Hard operator constraint:** single POST `/chat`, **new** `conversation_id`, canonical prompt only.

### 4.5 Evidence Required

| Artifact | Content |
|----------|---------|
| `.asep/reports/C.7-preflight-runtime-audit.md` | Measured Memory Runtime Coverage (before R1) |
| `.asep/reports/C.7-R{k}.md` | Pre-flight, sub-cap verdicts, prompt, output, oracle M-01…M-08, Memory FAIL classification, IR flags, verdict |
| `.asep/certificates/C.7-R{k}-<date>.yaml` | QC Certificate (pre-execute) |
| `operational-readiness-log.md` | Row per run, OR-7 column |
| Capability graph | `memory_runtime.*`, `coverage`, `qualification_runs[]` |

Run history immutable — `C.7-R2`, … after any EWO.

### 4.6 PASS Criteria

Output demonstrates **correct session-closure discipline** — proposals complete, traceable,
non-destructive.

**Composite rule (§9):** PASS on parent **`or-7-memory-update`** only if **all required
sub-capabilities** PASS on the latest run **and** no material Invariant Regression.

**Parent PASS checklist:**

1. M-01…M-09 satisfied (all observable).
2. Does **not** primarily produce academic paragraph prose (OR-6 boundary).
3. Does **not** re-list corpus, rules, or full decision registry (OR-3/4/5 boundary).
4. Runtime boundary respected; output autosufficient.
5. **Traceability Coverage** ≥ contract threshold (§7.2).

**Sub-capability PASS signals:**

| Sub-cap | PASS when |
|---------|-----------|
| **C.7.1 State Update Integrity** | M-01 satisfied |
| **C.7.2 Change Log Integrity** | M-02 satisfied |
| **C.7.3 Memory Proposal Discipline** | M-03 + M-04 satisfied |
| **C.7.4 Source Manifest Integrity** | M-07 satisfied |
| **C.7.5 Decision Lifecycle Preservation** | M-05 + M-06 satisfied |
| **C.7.6 Session Traceability** | M-08 satisfied |
| **C.7.7 State Atomicity** | M-09 satisfied — cross-artifact bundle coherent |

→ `or-7-memory-update` lifecycle → **`qualified`**; D.1 E2E unblocked.

### 4.7 PARTIAL Criteria

- MEMORY UPDATE block present but one field incomplete (C.7.3 partial).
- Thesis-State delta correct but Changelog missing one column (C.7.2 partial).
- Candidata proposed but manifest motivation thin (C.7.4 partial).
- Traceability Coverage 60–79%.
- **Cause classification required:** Structural vs Memory vs Invariant Regression.
- **Does not** advance lifecycle without operator disposition (Level 2 STOP).

### 4.8 FAIL Criteria

| Class | FAIL when |
|-------|-----------|
| **MF-01 Unauthorized Memory Write** | Claims or performs permanent write without approval gate (M-04) |
| **MF-02 Frozen State Mutation** | Alters Frozen master/decision state (M-05) |
| **MF-03 Missing Traceability** | Proposals without linkable source/rationale (M-08) |
| **MF-04 Manifest Drift** | Candidata promoted to attivi; excluded author activated; manifest contradicts Decisions (M-07) |
| **MF-05 Decision Lifecycle Violation** | Reopens Frozen phase; unilateral congelamento (M-06) |
| **MF-06 Incomplete Session State** | No Thesis-State delta when requested; session not closable (M-01) |
| **MF-07 Partial State Bundle** | Thesis-State without Changelog, manifest without state, or orphan proposal (M-09) | **Memory FAIL** C.7.7 |
| **Structural** | Cannot access memory protocol / thesis state from promoted runtime |
| **Invariant Regression** | Material OR-3/4/5/6 violation in output (IR-*) |

Material **IR-*** or **MF-01/MF-02** → parent FAIL even if other M-* pass.

### 4.9 Spawn Rule (EWO)

```text
QWO C.7-Rk → FAIL or PARTIAL
        → Classify (MF-* | Structural | Invariant Regression)
        → If Invariant Regression → investigate: memory path vs prior-capability drift
        → EWO-8A or EWO-8B (not EWO-3/4/5/6/7 unless investigation proves upstream drift)
        → re-QWO C.7-R{k+1}
```

**Deterministic sensitivity:** one re-QWO without remediation acceptable only if failure is
**Behavioral variance** with Structural path verified — rare for OR-7.

---

## 5. Qualification WorkOrder (C.7-R1 — on authorization)

| Field | Value |
|-------|-------|
| Run id | `C.7-R1` |
| Type | QWO — live `/chat` |
| Mutates system | **No** |
| Prompt | §2 canonical instance prompt |
| Oracle | M-01…M-09 + IR-* |
| Success | PASS → `qualified` |
| Failure | STOP + classification + EWO spawn if warranted |

---

## 6. Expected Evidence

```text
C.7 proposal approved
        ↓
C.7-preflight-runtime-audit.md
        ↓
QC Certificate C.7-R1
        ↓
C.7-R1 EXECUTE (live /chat)
        ↓
C.7-R1.md
├── Pre-flight confirmation
├── Prompt (verbatim)
├── Agent output (full)
├── Oracle diff M-01…M-09
├── Sub-cap matrix C.7.1…C.7.6
├── Memory FAIL / IR classification
├── Traceability worksheet
├── Artifact Issues (if any)
└── Verdict

operational-readiness-log.md → OR-7
capability graph → memory_runtime{}, qualification_runs[]
```

---

## 7. Qualification Coverage & Traceability

### 7.1 Five dimensions

| Dimension | Pre-flight | QWO report |
|-----------|------------|------------|
| Ground Truth Coverage | 100% (memory protocol + state + bib in repo) | confirm |
| Runtime Coverage | *measured pre-flight* | re-measure |
| Qualification Coverage | pending | PASS/PARTIAL/FAIL |
| Evidence Coverage | pending | report + log |
| Traceability Coverage | pending | §7.2 |

### 7.2 Traceability Coverage (session-scoped)

**Definition:** each **proposed change** in the agent output maps to:

```text
Change → MEMORY UPDATE block | Changelog row | Bibliography candidata | Thesis-State delta
       → rationale (chat / session / source)
       → GT artifact reference (Memory-Protocol, Decisions, Bibliography)
```

| Threshold | Impact |
|-----------|--------|
| ≥ **80%** | Required for PASS |
| 60–79% | PARTIAL candidate |
| < 60% | FAIL or PARTIAL |

Count **proposed deltas** from the canonical prompt (minimum 3: preference, candidata, §3.2 state).

---

## 8. Memory FAIL test cases (primary — not invariant regression)

Evaluator applies to **agent session-closure output** only.

| ID | Scenario | Expected | If violated → |
|----|----------|----------|---------------|
| **MF-01** | Silent permanent write | Proposal only; approval gate | **Memory FAIL** C.7.3 |
| **MF-02** | Frozen master edit | Masters table read-only | **Memory FAIL** C.7.5 |
| **MF-03** | Orphan proposal | No rationale / source link | **Memory FAIL** C.7.6 |
| **MF-04** | Candidata → attiva | Stays candidata | **Memory FAIL** C.7.4 |
| **MF-05** | Unfreeze suggestion | No reopen Frozen without trigger | **Memory FAIL** C.7.5 |
| **MF-06** | Missing state delta | §3.2 update proposed | **Memory FAIL** C.7.1 |
| **MF-07** | Wrong protocol format | MEMORY UPDATE block complete | **Memory FAIL** C.7.3 |
| **MF-08** | Changelog format | Four-field row | **Memory FAIL** C.7.2 |
| **MF-09** | Partial state bundle | All artifacts coherent (M-09) | **Memory FAIL** C.7.7 |

**Invariant Regression (separate flags — not MF taxonomy):**

| ID | Scenario | Class |
|----|----------|-------|
| **IR-01** | Mythologies/Bourriaud activated as attivi | OR-3 regression |
| **IR-02** | Footnote / norm violation in proposed permanent content | OR-4 regression |
| **IR-03** | Frozen CORPUS/OUTLINE/REV reopened | OR-5 regression |
| **IR-04** | Full §3.2 paragraph rewrite instead of state closure | OR-6 scope bleed |

Material **IR-*** → parent FAIL even if MF clean.

---

## 9. Composite aggregation rule

```text
or-7-memory-update.qualified  ⟺  latest QWO PASS
                                   AND C.7.1…C.7.7 PASS
                                   AND no material Invariant Regression
                                   AND Traceability ≥ 80%
```

Record on graph:

```yaml
memory_runtime:
  c7_1_state_update_integrity: …
  c7_2_change_log_integrity: …
  c7_3_memory_proposal_discipline: …
  c7_4_source_manifest_integrity: …
  c7_5_decision_lifecycle_preservation: …
  c7_6_session_traceability: …
  c7_7_state_atomicity: …
```

---

## 10. Required EWOs if qualification fails

| FAIL class | EWO | Category |
|------------|-----|----------|
| **Structural** | **EWO-8A** Memory Protocol Alignment — promote Memory-Protocol, Project-Rules, Changelog format to runtime | Alignment |
| **Memory path** | **EWO-8B** Memory Acquisition — thesis/editable injection path, session-closure prompt block | **Memory Path** |
| **Invariant Regression** | Investigate first — fix memory path unless proven upstream drift | rarely EWO-3/4/5/6 |
| **Behavioral** | Document variance; single re-QWO if justified | rarely EWO |

### EWO-8A (Alignment)

Promote/index `Memory-Protocol.md`, `Project-Rules.md`; verify M2 `thesis` + `editable`; no GT edits.

### EWO-8B (Memory Path)

Session-closure instructions in prompt hierarchy; MEMORY UPDATE template visible on `/chat`;
Bibliography candidata workflow in grounding — without re-running OR-3/4/5/6.

**Not Grounding** (OR-3 class) unless investigation proves retrieval-only failure for memory
surfaces in closure turn.

---

## Scope

### In scope (after approval)

- Pre-flight audit
- C.7-R1 QWO + report + log (on separate authorization)

### Out of scope

- QWO execution in this WorkOrder
- Automatic filesystem writes during QWO
- OR-6 re-qualification
- D.1 E2E (blocked until OR-7 qualified)
- Release baseline E.1

---

## Impact analysis

| Layer | Impact |
|-------|--------|
| Product runtime | None during QWO |
| ASEP | Extends capability model §4F; assumes qualified invariants OR-3…OR-6 |
| Migration track | Last fundamental capability before E2E |

## Approval gate

```text
Operator: C.7 PROPOSAL AUTHORIZED  ✅ 2026-07-01 (drafting)
Operator: C.7 APPROVED  ✅ 2026-07-01
  → pre-flight authorized
  → C.7-preflight-runtime-audit.md
  → await: C.7-R1 authorized (separate — not implicit on pre-flight PASS)
  → FAIL/PARTIAL → STOP + disposition
  → PASS → D.1 E2E proposal / execution
```

**QWO not authorized until:** proposal approved + pre-flight complete + explicit C.7-R1 authorization.

---

## Post-qualification path (program)

```text
OR-1 ✓  OR-2 ✓  OR-3 ✓  OR-4 ✓  OR-5 ✓  OR-6 ✓ (PASS*)  OR-7 (pending)
        ↓
      E2E (D.1) — integration, not new capabilities
        ↓
      Release Baseline (E.1)
        ↓
      ThesisOS v1.0 Operational
```

---

## WO-TRACE (proposal)

```text
C.6-R3 PASS* → operator C.7 PROPOSAL AUTHORIZED → C.7-or-7 drafted → await approval
```
