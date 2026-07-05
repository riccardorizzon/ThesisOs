# Qualification WorkOrder Proposal — C.5

> **Status:** ✅ **Approved with refinement** · **C.5-R1 PASS** · `or-5-decisions` **qualified** (2026-06-30)
>
> **META-1:** ✅ APPROVED — baseline (`docs/asep-capability-model.md`)  
> **Program:** `.asep/programs/thesis-agent-migration.yaml`  
> **Spec instance:** `knowledge/thesis-agent/_migration/operational-readiness.md` § OR-5  
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
| 8 | Organizational FAIL test cases | §8 |
| 9 | Composite capability aggregation rule | §9 |
| 10 | Required EWOs if qualification fails | §10 |

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | C.5 |
| **Type** | **QWO** (Qualification WorkOrder) — validation only |
| **Platform capability class** | **Decision Lifecycle Integrity** |
| **Knowledge domain** | **Organizational** |
| **Graph node** | `or-5-decisions` |
| **QWO sensitivity** | **Deterministic** |
| **Lifecycle transition** | `specified` → **`approved`** (2026-06-30, with refinement) → `qualified` (on PASS) |
| **Program** | `thesis-agent-migration` · run `kimi-claw-2026-06` |
| **Depends on** | `or-4-rules` **qualified** (C.4-R1 PASS, 2026-06-30) |
| **First run id** | `C.5-R1` (on approval) |

---

## 1. Platform objective (ASEP — program-agnostic)

Qualify the generic ASEP capability **Decision Lifecycle Integrity**:

> The live runtime treats **decisions** as **governed objects** (Decision Object) with an
> explicit lifecycle — not as facts, corpus entries, or normative rules — and can **acquire**,
> **recognize lifecycle state**, **preserve closure**, and **maintain decision consistency**
> (no decision used in a state incompatible with its lifecycle) without conflating
> Organizational knowledge with Scientific or Normative domains.

### 1.1 Decision ≠ fact

| Kind | Meaning | Example | OR gate |
|------|---------|---------|---------|
| **Fact** | Observable state of an artifact | «Outline-Master v1.0 exists in repo» | OR-1 |
| **Norm** | Rule constraining behaviour | «Footnotes vietate» (UNI-01 §8) | OR-4 |
| **Decision** | Governed commitment with lifecycle | «CORPUS-02: Mythologies escluso — Congelato» | **OR-5** |

A decision may **reference** facts and norms; qualifying OR-5 verifies the agent **honours
the decision object's state**, not merely that it knows the underlying content.

### 1.2 Decision lifecycle model (platform)

Program-agnostic lifecycle for governed decisions:

```text
Draft → Approved → Frozen → Deprecated → Removed
```

| State | Meaning | Agent obligation when reporting |
|-------|---------|--------------------------------|
| **Draft** | Proposed, not binding | Label as non-binding; do not treat as closed |
| **Approved** | Accepted, may still evolve | Distinguish from frozen; cite approval context |
| **Frozen** | Closed — changes require explicit trigger | Must not suggest reopening without trigger |
| **Deprecated** | Superseded — retained for audit | Cite successor decision if known |
| **Removed** | Revoked — no longer applies | Must not apply or cite as binding |

**ThesisOS instance mapping:** GT uses «Congelato» ≈ **Frozen**, «Da decidere» / open items ≈
**Draft** or pre-**Approved**, «Approvato» (PLAT-*) ≈ **Approved**. Full Deprecated/Removed
states are **framework-ready**; instance QWO tests **Frozen vs open** primarily.

### 1.3 Decision Object (ASEP framework entity)

Alongside Capability, WorkOrder, Evidence, and Ground Truth, ASEP now formalizes the
**Decision Object** — program-agnostic, not ThesisOS-specific:

```text
Decision Object
├── id              (e.g. CORPUS-02, REV-006)
├── domain          (organizational | normative | scientific | procedural)
├── owner           (operator | relatrice | institution | system)
├── state           (Draft | Approved | Frozen | Deprecated | Removed)
├── created_by      (WorkOrder / operator gate)
├── supersedes      (optional prior decision id)
├── superseded_by   (optional successor id)
├── rationale       (why the decision exists)
├── evidence        (report / WO-TRACE link)
├── effective_from  (optional)
└── effective_until (optional)
```

The lifecycle diagram (§1.2) is the **state machine of this entity**, not a prose label.
Future ASEP may add: automatic supersession, decision audit, controlled rollback, impact
analysis — **out of scope for C.5 QWO**.

**Capability vs governance policy (refinement):**

| Layer | What it is | Example |
|-------|------------|---------|
| **Capability** | What the runtime can **do** with Decision Objects | Recognize Frozen; detect inconsistent use |
| **Governance policy** | What operators **must not do** without a trigger | «Non riproporre corpus stress test senza trigger» |

Governance policies are **consequences** of frozen decisions — tested **via** C.5.4 Decision
Consistency, not as a separate sub-capability named after the policy.

**Not in scope of platform capability:**

- Scientific corpus utilization (OR-3)
- Normative constraint compliance (OR-4)
- Procedural methodology explanation (OR-2)

---

## 2. Program instance binding (ThesisOS migration — not ASEP core)

Maps abstract sub-capabilities to this program's **Organizational** Ground Truth.

| Abstract (ASEP) | ThesisOS instance |
|-----------------|---------------------|
| **DecisionRegistry** | `03_PROJECT/Decisions.md` |
| **ProjectStateSnapshot** | `03_PROJECT/Thesis-State.md` |
| **DecisionChangelog** | `05_MEMORY/Changelog.md` |
| **RuntimeDecisionSurface** | M2 `decisions` memory + M2 `thesis` (artifact freeze table) |
| **Frozen phase labels** | CORPUS v2.1 · BIBLIOGRAFIA v1.0 · OUTLINE v1.0 · META-DOCUMENTI (STIGMATA framework v1.0) |

**Canonical QWO prompt (instance — extends OR-5 spec with lifecycle vocabulary):**

```text
Quali decisioni di progetto sono congelate e quali restano aperte? Per ciascuna indica
lo stato nel ciclo di vita (congelata / aperta). Cosa non si deve riproporre senza
trigger esplicito?
```

**Evaluator oracle (instance):** `Decisions.md`, `Thesis-State.md`, `Changelog.md`,
M2 promoted `decisions` / `thesis` memories.

---

## 3. Composite capability decomposition

Parent node: **`or-5-decisions`** (composite).

| Sub-capability | ASEP meaning | ThesisOS QWO signal |
|----------------|--------------|---------------------|
| **C.5.1 Decision Acquisition** | Organizational GT present in runtime | Agent can list decisions traceable to `Decisions.md` / M2 `decisions` |
| **C.5.2 Lifecycle State Recognition** | Maps each cited decision to correct lifecycle state | «Congelato» vs «Da decidere» / open; no Draft labeled Frozen |
| **C.5.3 Closure Integrity** | Frozen set complete and accurate for tested scope | CORPUS/REV/METH/UNI/REL frozen; open items from § Da decidere |
| **C.5.4 Decision Consistency** | No decision **used** in a state incompatible with its lifecycle | Frozen CORPUS-02 cited as «open»; Frozen phase treated as Draft in recommendations |

**C.5.4 is a capability**, not a governance policy. The policy «non riproporre senza trigger»
is evaluated as a **symptom of inconsistency** when the agent treats a **Frozen** decision
as if it were **Draft/Approved** (e.g. suggests redoing corpus stress test = using CORPUS
phase as non-Frozen).

Future graph refactor may split child nodes; until then sub-cap status is recorded on the parent.

---

## 3.1 Runtime Coverage — governance rule (same as C.4)

**Runtime Coverage is observed at pre-flight; it is not a contract presupposition.**

```text
Proposal (approved)
        ↓
Pre-flight Runtime Audit
        ↓
Measured Runtime Coverage   ← authorizes C.5-R1
        ↓
QWO (C.5-R1)
```

Proposal-time estimates are **informative only**. PASS criteria depend on **agent output vs
Ground Truth**, not on a pre-declared coverage percentage.

### 3.3 Artifact Issue taxonomy (parallel — not FAIL taxonomy)

**Artifact Issues** classify problems in **evidence artifacts** (reports, labels, metadata).
They are **orthogonal** to capability FAIL classes — never spawn EWO by default.

```text
Artifact Issue
├── Documentation Defect    (wrong ID label; substance OK — e.g. C.4-R1 REL-03 slip)
├── Metadata Defect         (wrong version/state tag on artifact)
└── Formatting Defect       (presentation / structure only)
```

Record in QWO report under **Artifact Issues** section — **not** under Organizational FAIL.
Precedent: C.4-R1 REL-03 → **Documentation Defect**; no EWO.

### 3.4 Readiness Vector (future — META-2 candidate)

Pre-flight today records **Measured Runtime Coverage**. A future evolution may add a
multidimensional **Readiness Vector** (GT / Runtime / Supervisor / QC / Policy / Traceability)
reusable across OR-5…OR-7. **Not required for C.5** — documented for framework evolution only.

---

## 4. Qualification Contract

### 4.1 Capability

`or-5-decisions` — **Decision Lifecycle Integrity** on **Organizational** knowledge (platform class).

### 4.2 Prerequisiti

| Precondition | Expected state | Verification |
|--------------|----------------|--------------|
| META-1 approved | Capability model baseline | `docs/asep-capability-model.md` |
| `or-4` qualified | C.4-R1 PASS | capability graph |
| `or-3` qualified | C.3-R4 PASS | capability graph |
| Phase B + EWO-1 | `decisions` + `thesis` memories promoted | `promotion-log.md`, EWO-1 report |
| Live stack | `/health` → 200 | pre-flight |
| **Pre-flight audit** | **Measured** Runtime Coverage recorded | `.asep/reports/C.5-preflight-runtime-audit.md` (before R1) |
| Proposal approved | this document → approved | **User explicit approval** |
| **QWO authorization** | Pre-flight complete + measured coverage on record | gates **C.5-R1** only — not PASS |

### 4.3 Ground Truth (evaluator only)

**Platform rule:** Organizational GT = frozen artifacts whose primary purpose is to record
**governed commitments**, phase closure, and open decision backlog. Format-agnostic.

**ThesisOS binding:**

| Priority | Artifact | Role |
|----------|----------|------|
| **Primary** | `03_PROJECT/Decisions.md` | Decision registry: CORPUS/REV/METH/UNI/REL/RED/MEM/PLAT + cronologia fasi + **Da decidere** |
| **Primary** | `03_PROJECT/Thesis-State.md` | Master artifact freeze table; stesura state; domanda GT |
| **Binding** | `05_MEMORY/Changelog.md` | Decision/state change trail |
| **Auxiliary** | `03_PROJECT/TODO.md` | Backlog mirror — subordinate to Decisions.md |

**Mandatory GT elements for PASS (instance oracle checklist):**

| ID | Element | Lifecycle signal |
|----|---------|------------------|
| D-01 | Fase **CORPUS** congelata (v2.1 / Core-Theory-Map) | **Frozen** |
| D-02 | Fase **BIBLIOGRAFIA** congelata (v1.0) | **Frozen** |
| D-03 | Fase **OUTLINE** congelata (v1.0) | **Frozen** |
| D-04 | Fase **META-DOCUMENTI** / STIGMATA framework congelata (v1.0) | **Frozen** |
| D-05 | **CORPUS-02** (Mythologies) + **CORPUS-03** (Bourriaud) esclusi — congelati | **Frozen** |
| D-06 | **REV-001–006** congelate | **Frozen** |
| D-07 | **METH-02** STIGMATA caso applicativo — congelato | **Frozen** |
| D-08 | Open items from **§ Da decidere** (≥3: checklist §13, M6 auto-persist, reimport cap. 1–2) | **Open / Draft** |
| D-09 | **Decision Consistency:** no Frozen decision used as if Draft/Approved (symptom: reopen corpus/bibliografia/stress test) | **Consistency** |
| D-10 | Distinguishes **decision object** vs **fact** (e.g. «file exists» vs «decision to freeze») | Recognition |
| D-11 | Does **not** conflate OR-3 corpus list with OR-5 decision closure | Domain boundary |
| D-12 | No invented frozen or open decisions | Governance |

### 4.4 Runtime Boundary

**Agent under test must NOT use:**

- Workspace `knowledge/thesis-agent/` (blueprint)
- Export `_inbox/kimi-claw/`
- Web / external sources
- Operator paste of Decisions from clipboard
- File attachments on `/chat`

**Allowed runtime surfaces (only):**

| Surface | Expected contribution |
|---------|----------------------|
| M2 `decisions` | Full decision registry (CORPUS/REV/METH/UNI/REL/…) |
| M2 `thesis` | Thesis-State snapshot; master artifact table |
| M2 `editable` | Project overlay (subordinate) |
| M3/M4 documents | Promoted masters if indexed — auxiliary, not substitute for `decisions` memory |

**Hard operator constraint:** single POST `/chat`, **new** `conversation_id`, canonical prompt only.

### 4.5 Evidence Required

| Artifact | Content |
|----------|---------|
| `.asep/reports/C.5-preflight-runtime-audit.md` | Measured Organizational Runtime Coverage (before R1) |
| `.asep/reports/C.5-R{k}.md` | Pre-flight, five Coverage dimensions, sub-cap verdicts, prompt, output, oracle diff, Organizational FAIL classification, verdict |
| `.asep/certificates/C.5-R{k}-<date>.yaml` | QC Certificate (pre-execute) |
| `operational-readiness-log.md` | Row per run, OR-5 column |
| Capability graph | `decision_lifecycle.*`, `coverage`, `qualification_runs[]` |

Run history immutable — `C.5-R2`, … after any EWO.

### 4.6 PASS Criteria

Output fedele al Organizational Ground Truth, ricostruibile dalle sorgenti promosse.

**Composite rule (§9):** PASS on parent **`or-5-decisions`** only if **all required sub-capabilities** PASS on the latest run.

**Parent PASS checklist:**

1. Lists **frozen phases** D-01–D-04 (CORPUS, BIBLIOGRAFIA, OUTLINE, META-DOCUMENTI/STIGMATA).
2. Lists **key frozen decision IDs** D-05–D-07 (CORPUS-02/03, REV set, METH-02) with **Frozen** semantics.
3. Lists **open decisions** D-08 from § Da decidere — not fewer than GT open set; not mislabeled as frozen.
4. **Decision Consistency** D-09: no Frozen decision treated as open — e.g. no corpus stress-test redo or bibliography reopen (incompatible lifecycle use).
5. **Decision vs fact** D-10: decisions framed as governed Decision Objects, not mere file descriptions.
6. **Domain boundary** D-11: no substitution of OR-3 corpus enumeration for decision closure.
7. No **invented** decisions D-12.
8. Runtime boundary respected; output autosufficient.
9. **Traceability Coverage** ≥ contract threshold (§7.2).

**Sub-capability PASS signals:**

| Sub-cap | PASS when |
|---------|-----------|
| **C.5.1 Acquisition** | ≥85% of oracle elements D-01–D-08 appear with runtime-traceable anchor |
| **C.5.2 Lifecycle State Recognition** | Frozen vs open labels correct; ≤1 material mis-label |
| **C.5.3 Closure Integrity** | D-01–D-07 substantially complete; open set matches GT |
| **C.5.4 Decision Consistency** | D-09 satisfied: no material lifecycle-incompatible use of Frozen decisions |

→ `or-5-decisions` lifecycle → **`qualified`**; OR-6 unblocked (C.6 proposal).

### 4.7 PARTIAL Criteria

- Correct **frozen subset** + **decision consistency** OK, but open backlog incomplete (C.5.3 gap).
- REV or phase labels present but **lifecycle vocabulary** inconsistent (C.5.2 partial).
- Traceability Coverage 60–79%.
- **Cause classification required:** Structural vs Organizational vs Reasoning (Artifact Issues recorded separately).
- **Does not** advance lifecycle without operator decision (Level 2 STOP).

### 4.8 FAIL Criteria

| Class | FAIL when |
|-------|-----------|
| **Structural** | Cannot reconstruct decision registry from promoted sources alone |
| **Organizational** | Treats open item as frozen, or uses Frozen decision inconsistently (D-09 / C.5.4) |
| **Governance** | Invents binding decisions not in GT |
| **Behavioral** | Non-deterministic omission without structural cause |
| **Domain bleed** | Answers as OR-3 corpus QWO ignoring decision lifecycle (D-11 material) |

**Material divergence examples:**

- Suggests redoing corpus stress test or expanding bibliography without approval trigger.
- Lists Mythologies/Bourriaud as «to be decided» when CORPUS-02/03 are frozen.
- Omits all open items from § Da decidere while claiming completeness.
- Violates runtime boundary.

### 4.9 Spawn Rule (EWO)

```text
QWO C.5-Rk → FAIL or PARTIAL
        → Classify (Structural | Organizational | Acquisition | Behavioral | Governance)
        → Artifact Issues noted separately (§3.3) — not FAIL class
        → Investigation if ambiguous
        → EWO proposal (EWO-6A Alignment | EWO-6B Decision Acquisition)
        → NO patch during QWO
        → re-QWO C.5-R{k+1}
```

**Terminology rule:** do **not** use **Grounding** for OR-5 remediation (reserved for OR-3 Scientific domain).

### 4.10 Lifecycle Transition

| Verdict | Capability lifecycle | OR-5 log | Unblocks |
|---------|---------------------|----------|----------|
| **PASS** | → `qualified` | PASS | C.6 / OR-6 |
| **PARTIAL** | unchanged | PARTIAL | operator disposition |
| **FAIL** | unchanged | FAIL | EWO if structural/organizational |

---

## 5. Qualification WorkOrder (execution definition)

**Gate:** C.5-R1 may start only after pre-flight records **measured** Runtime Coverage.

| Phase | Action | Mutations |
|-------|--------|-----------|
| **PLAN** | Confirm proposal approved + pre-flight complete | none |
| **QC** | Issue certificate `.asep/certificates/C.5-R1-<date>.yaml` | none |
| **Policy** | Level 2 auto-authorize QWO if clauses met | none |
| **EXECUTE** | POST `/chat` canonical prompt; new session | none |
| **VERIFY** | Oracle diff vs §4.3; sub-cap matrix; Traceability; Organizational FAIL tests | none |
| **REPORT** | Write `.asep/reports/C.5-R1.md`; update graph + log | evidence only |
| **STOP** | On PARTIAL/FAIL — operator disposition; no auto-accept | — |

**Duration budget:** single turn; **Deterministic** sensitivity (low variance vs OR-3).

---

## 6. Expected evidence (post-run artifacts)

```text
C.5-preflight-runtime-audit.md
        ↓
C.5-R1.md
├── Pre-flight (/health, measured organizational runtime coverage)
├── Canonical prompt (verbatim)
├── Agent output (integral or summary + char count)
├── Sub-capability matrix (C.5.1–C.5.4: PASS/PARTIAL/FAIL)
├── Oracle diff table (D-01…D-12)
├── Organizational FAIL test case results (§8)
├── Five Coverage dimensions (§7)
├── Traceability worksheet (§7)
├── Artifact Issue notes (§3.3 — if any; non-blocking)
├── FAIL class if applicable
├── WO-TRACE line
└── Verdict + lifecycle recommendation

operational-readiness-log.md  →  OR-5 row
capability graph              →  qualification_runs[], decision_lifecycle{}, coverage{}
```

---

## 7. Qualification Coverage & Traceability Coverage

### 7.1 Five dimensions (record all in QWO report)

| Dimension | At proposal | At pre-flight | At QWO report |
|-----------|-------------|---------------|---------------|
| **Ground Truth Coverage** | 100% (repo) | confirm | confirm |
| **Runtime Coverage** | *informative estimate* | **measured** | re-measure |
| **Qualification Coverage** | pending | pending | PASS/PARTIAL/FAIL |
| **Evidence Coverage** | pending | pre-flight artifact | report + log |
| **Traceability Coverage** | pending | pending | §7.2 |

**Informative pre-flight estimate (not authoritative — audit before R1):**

| GT element | Expected surface | Notes |
|------------|------------------|-------|
| `Decisions.md` registry | M2 `decisions` | Fase B promoted (~4500 chars) |
| `Thesis-State.md` | M2 `thesis` | EWO-1 patched |
| `Decisions.md` as M3 doc | likely absent | Same pattern as C.4 digest docs |
| `Changelog.md` | repo only unless promoted | May reduce traceability for D-08 history |

Pre-flight script/checklist required — mirror C.4 / EWO-3 audit pattern.

### 7.2 Traceability Coverage metric (contract)

**Definition:** fraction of **scored organizational claims** mappable through:

```text
Claim → decision ID (CORPUS-NN, REV-NNN, …) OR phase label OR [BINDING DECISIONS]
      → promoted runtime artifact
      → Decisions.md / Thesis-State.md section
```

| Metric | Weight | Formula |
|--------|--------|---------|
| Decision ID anchors | 40% | claims with valid ID / total decision claims |
| Lifecycle labels correct | 30% | correct Frozen/Open / total labeled |
| Oracle element trace | 30% | D-01…D-12 traceable / 12 |

**Traceability Coverage** = weighted sum (0–100%).

| Threshold | Verdict impact |
|-----------|----------------|
| ≥ **80%** | Required for **PASS** (with other criteria) |
| 60–79% | **PARTIAL** candidate |
| < 60% | **FAIL** or PARTIAL with Acquisition gap |

---

## 8. Organizational FAIL test cases (oracle — evaluator applies post-run)

Classification probes — not separate QWO runs.

| ID | Scenario | Expected compliant behaviour | If violated → |
|----|----------|------------------------------|---------------|
| **OF-01** | Lifecycle-incompatible use (corpus) | Treats Frozen CORPUS phase as open → suggests stress-test redo | **Organizational FAIL** (C.5.4) |
| **OF-02** | Lifecycle-incompatible use (biblio) | Treats Frozen BIBLIOGRAFIA as open → suggests expansion | **Organizational FAIL** (C.5.4) |
| **OF-03** | Frozen mis-label | CORPUS-02/03 listed as «open» or «candidate» | **Organizational FAIL** (C.5.2) |
| **OF-04** | Open omission | § Da decidere items absent while claiming full closure | **Organizational FAIL** (C.5.3) |
| **OF-05** | Decision vs fact | Describes only file paths without decision state | **Organizational FAIL** (C.5.2) |
| **OF-06** | OR-3 bleed | Primary answer is author list (OR-3) not decision closure | **Domain bleed FAIL** (D-11) |
| **OF-07** | Invented decision | Cites decision ID not in `Decisions.md` | **Governance FAIL** |
| **OF-08** | Inconsistent recommendation | Language implying Frozen decision is actionable as Draft | **Organizational FAIL** (C.5.4) |
| **OF-09** | Structural ghost | Correct decisions stated but none traceable to M2 `decisions` | **Structural FAIL** |
| **OF-10** | ID / metadata slip | Wrong decision ID label; substance OK | **Artifact Issue → Documentation Defect** (non-blocking) |

**PASS constraint:** zero **material** OF-01–OF-09 failures.

---

## 9. Composite capability aggregation rule

```text
or-5-decisions.qualified  ⟺  latest QWO run verdict PASS
                              AND C.5.1 PASS
                              AND C.5.2 PASS
                              AND C.5.3 PASS
                              AND C.5.4 PASS
                              AND Traceability Coverage ≥ 80%
```

| Latest run | Sub-cap states | Parent lifecycle |
|------------|----------------|------------------|
| PARTIAL | any sub-cap PARTIAL/FAIL | **unchanged** |
| PASS | one sub-cap PARTIAL | **PARTIAL** overall — operator gate |
| PASS | all sub-cap PASS | **`qualified`** |

**Regression isolation:**

- Fail **C.5.4** only → reopen Decision Consistency; do not re-run OR-3/4.
- Fail **C.5.1** → **EWO-6A** Alignment; re-QWO acquisition only.

Record on graph:

```yaml
decision_lifecycle:
  c5_1_acquisition: <pending|partial|qualified|fail>
  c5_2_state_recognition: …
  c5_3_closure_integrity: …
  c5_4_decision_consistency: …
```

---

## 10. Required Engineering WorkOrders if qualification fails

| FAIL class | Primary cause | EWO | Category |
|------------|---------------|-----|----------|
| **Structural** | Decision registry not in runtime / not searchable | **EWO-6A** Organizational Alignment | **Alignment** |
| **Organizational** | GT present; agent mis-states lifecycle or suggests reopening | Investigate → **EWO-6B** Decision Acquisition | **Decision Acquisition** |
| **Acquisition** | M2 `decisions` not in prompt / retrieval path | **EWO-6B** | **Decision Acquisition** |
| **Behavioral** | Variance without structural change | Robustness note; single re-QWO if Traceability OK | rarely EWO |
| **Governance** | Invents decisions | Fix governance; **no** auto-EWO | — |

**Artifact Issues (§3.3)** are recorded in the report but **not** routed through this FAIL/EWO table.

### EWO-6A (candidate — Alignment)

**Trigger:** C.5-Rk FAIL/PARTIAL + Structural + measured Runtime Coverage gap.

**Scope:**

- Promote / refresh M2 `decisions` from `Decisions.md`
- Optional M3 upload of `Decisions.md` digest for search
- Verify `thesis` memory includes Thesis-State master table
- Coherence audit + idempotent script (mirror EWO-1/3 pattern)
- **No** GT content edits

### EWO-6B (candidate — Decision Acquisition)

**Trigger:** Measured Runtime Coverage adequate but C.5.1–C.5.3 FAIL — decisions present but not **acquired** into agent context.

**Scope:**

- Decision registry block in prompt hierarchy (organizational layer — parallel to normative/scientific)
- Optional retrieval boost for decision-list / frozen-phase queries
- **Not** Grounding (OR-3) · **Not** Constraint Acquisition (OR-4)
- **No** GT edits

```text
C.5-R1 FAIL/PARTIAL
  → Investigation (if Organizational vs Structural ambiguous)
  → EWO-6A or EWO-6B (not both without evidence)
  → C.5-R2
```

---

## Scope

### In scope (after approval)

- Pre-flight organizational runtime audit
- C.5-R1 live QWO + evaluation + report + log + graph update

### Out of scope

- QWO execution in this proposal phase
- Qualification / lifecycle advance without PASS
- GT, thesis content, Constitution, ADR changes
- Full Deprecated/Removed lifecycle instances (framework-ready; instance tests Frozen/Open)
- OR-6, OR-7, E2E

---

## Impact analysis

| Layer | Impact |
|-------|--------|
| Product runtime | **None** during QWO |
| Capability graph | Evidence fields only post-QWO |
| ASEP core | Extends META-1 with Organizational sub-cap model; no Constitution change |

## Rollback

N/A — QWO is read-only validation.

## Approval gate

```text
User: C.5: approved (with refinement)  ✅ 2026-06-30
  → pre-flight audit authorized
  → C.5-R1 authorized after measured coverage (Level 2: QC + policy)
  → FAIL/PARTIAL → STOP + disposition (no auto-accept)
```

---

## Compatibility checklist

| Invariant | Status |
|-----------|--------|
| Engineering State Machine | ✅ `approved` → QWO → `qualified` on PASS |
| WO-TRACE | ✅ EWO before re-QWO on classified FAIL |
| Capability Graph | ✅ composite `or-5-decisions` + sub-cap fields |
| META-1 domain separation | ✅ Organizational ≠ Scientific ≠ Normative |
| Engineering Supervisor | ✅ STOP on PARTIAL/FAIL disposition |
| Quality Controller | ✅ certificate before EXECUTE |
| Auto Approval Policy | ✅ QWO conditional auto-auth; no auto-accept verdict |
| Termination Policy | ✅ T2 on PARTIAL; pre-flight gates QWO |

---

## Recommended next action

1. ~~User approves this proposal~~ ✅ **2026-06-30** (C.5.4 → Decision Consistency refinement)
2. Execute **C.5 pre-flight** organizational runtime audit (measured coverage)
3. Execute **C.5-R1** (QC + Level 2; no mutations)
4. **PASS** → `or-5-decisions` **qualified** → C.6 proposal  
   **FAIL/PARTIAL** → classify → EWO-6A / EWO-6B → re-QWO
