# Qualification WorkOrder Proposal — C.4

> **Status:** ✅ **Approved** · **C.4-R1 PASS** · `or-4-rules` **qualified** (2026-06-30)
>
> **META-1:** ✅ APPROVED — architecture baseline (`docs/asep-capability-model.md`)  
> **Program:** `.asep/programs/thesis-agent-migration.yaml`  
> **Spec instance:** `knowledge/thesis-agent/_migration/operational-readiness.md` § OR-4  
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
| 8 | Normative FAIL test cases | §8 |
| 9 | Composite capability aggregation rule | §9 |
| 10 | Required EWOs if qualification fails | §10 |

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | C.4 |
| **Type** | **QWO** (Qualification WorkOrder) — validation only |
| **Platform capability class** | **Constraint Compliance** |
| **Knowledge domain** | **Normative** |
| **Graph node** | `or-4-rules` |
| **QWO sensitivity** | **Deterministic** |
| **Lifecycle transition** | `specified` → **`approved`** (2026-06-30) → `qualified` (on PASS) |
| **Program** | `thesis-agent-migration` · run `kimi-claw-2026-06` |
| **Depends on** | `or-3-corpus` **qualified** (C.3-R4 PASS, 2026-06-30) |
| **First run id** | `C.4-R1` (on approval) |

---

## 1. Platform objective (ASEP — program-agnostic)

Qualify the generic ASEP capability **Constraint Compliance**:

> The live runtime can **acquire**, **interpret**, **enforce**, and **resolve conflicts**
> among **Normative Ground Truth** constraints — without conflating them with Scientific,
> Procedural, or Organizational knowledge.

This proposal defines the **Qualification Contract** and **Qualification WorkOrder**
for that capability. It is reusable across programs (thesis, contracts, ISO manuals,
compliance policies) by swapping **Program Instance Bindings** (§2) only.

**Not in scope of the platform capability:**

- Scientific corpus utilization (OR-3 / Knowledge Utilization)
- Procedural methodology (OR-2)
- Organizational decision closure (OR-5)

---

## 2. Program instance binding (ThesisOS migration — not ASEP core)

Maps abstract sub-capabilities to this program's Normative Ground Truth.

| Abstract (ASEP) | ThesisOS instance |
|-----------------|---------------------|
| **InstitutionalConstraintLayer** | `University-Rules.md` (UNI-01) ← guida Accademia del Lusso |
| **SupervisorConstraintLayer** | `Relatrice-Rules.md` (REL-01) — R1–R5 validated only |
| **ProjectPreferenceOverlay** | `Decisions.md` RED-02, REV-001–006; `Project-Rules.md` |
| **Conflict precedence** | Institutional (UNI) > validated supervisor (REL) > project editable > agent suggestion |

**Canonical QWO prompt (instance):**

```text
Elenca tutte le regole università e della relatrice attualmente applicabili alla
stesura. Distingui obblighi istituzionali da preferenze di progetto.
```

**Evaluator oracle (instance):** `University-Rules.md`, `Relatrice-Rules.md`,
`Decisions.md` (UNI-01, REL-01, REV-001–006, RED-02), `05_MEMORY/Permanent.md`.

---

## 3. Composite capability decomposition

Parent node: **`or-4-rules`** (composite).

| Sub-capability | ASEP meaning | ThesisOS QWO signal |
|----------------|--------------|---------------------|
| **C.4.1 Constraint Acquisition** | Normative GT present in runtime surfaces | Agent can list rules traceable to promoted UNI/REL artifacts |
| **C.4.2 Constraint Interpretation** | Distinguishes constraint **class** (institutional / supervisor / project) | Separates guida Accademia vs relatrice vs preferenza progetto (e.g. note vietate) |
| **C.4.3 Constraint Enforcement** | States **prohibitions and obligations** correctly when asked | No footnotes; autore-date; structure §3.1; no invented rules |
| **C.4.4 Constraint Conflict Resolution** | Applies **precedence** when layers disagree | UNI-01 footnote ban wins; REL defers to UNI where cited; no false "relatrice law" for project prefs |

Future graph refactor may split child nodes; until then sub-cap status is recorded on the parent.

---

## 3.1 Runtime Coverage — governance rule (META-1 refinement)

**Runtime Coverage is observed at pre-flight; it is not a contract presupposition.**

```text
Proposal (approved)
        ↓
Pre-flight Runtime Audit
        ↓
Measured Runtime Coverage   ← authorizes C.4-R1
        ↓
QWO (C.4-R1)
```

| Phase | Runtime Coverage role |
|-------|---------------------|
| **Proposal** | Informative estimate only (if any) — does **not** gate approval or PASS |
| **Pre-flight** | **Measured** value recorded; gates **QWO authorization** |
| **QWO report** | Re-measured post-run; complements verdict, does not replace PASS/PARTIAL/FAIL |

The Qualification Contract PASS criteria depend on **agent output vs Ground Truth**, not on a pre-declared coverage percentage.

---

## 4. Qualification Contract

### 4.1 Capability

`or-4-rules` — **Constraint Compliance** on **Normative** knowledge (platform class).

### 4.2 Prerequisiti

| Precondition | Expected state | Verification |
|--------------|----------------|--------------|
| META-1 approved | Capability model baseline | `docs/asep-capability-model.md` |
| `or-3` qualified | C.3-R4 PASS | capability graph |
| Phase A complete | UNI-01, REL-01 frozen | `Decisions.md`, post-migration validation |
| Phase B complete | Normative memories promoted | `promotion-log.md` (`university-rules`, `relatrice-rules`) |
| Live stack | `/health` → 200 | pre-flight |
| **Pre-flight audit** | **Measured** Runtime Coverage recorded | `.asep/reports/C.4-preflight-runtime-audit.md` ✅ **90%** |
| Proposal approved | this document → approved | ✅ **2026-06-30** |
| **QWO authorization** | Pre-flight complete + measured coverage on record | gates **C.4-R1** only — not PASS |

### 4.3 Ground Truth (evaluator only)

**Platform rule:** Normative GT = any frozen artifact whose primary purpose is to constrain
operator or system behaviour. Format-agnostic.

**ThesisOS binding:**

| Priority | Artifact | Role |
|----------|----------|------|
| **Primary — Institutional** | `03_PROJECT/University-Rules.md` (UNI-01) | Structure §3.1, length triennale, impaginazione, citazioni autore-data, **§8 no footnotes**, bibliografia, plagio |
| **Primary — Supervisor** | `03_PROJECT/Relatrice-Rules.md` (REL-01) | R1–R5 **validated only**; workflow relatrice |
| **Binding** | `03_PROJECT/Decisions.md` | UNI-01, REL-01, REV-001–006, RED-02 (footnote vietate) |
| **Auxiliary** | `03_PROJECT/Project-Rules.md`, `05_MEMORY/Permanent.md` | Project overlay; not substitute for UNI/REL primary text |
| **Auxiliary — source OCR** | `04_KNOWLEDGE/University/Guida-Redazione-Tesi.md` | Institutional source document if promoted; subordinate to `University-Rules.md` digest |

**Mandatory GT elements for PASS (instance oracle checklist):**

| ID | Element | Layer |
|----|---------|-------|
| N-01 | Tesi triennale ≥ 80.000 battute (orient. ~40 pp.) | Institutional |
| N-02 | Struttura ordine §3.1 (copertina … conclusione … bibliografia) | Institutional |
| N-03 | Citazioni **autore-data nel corpo** | Institutional |
| N-04 | **Nessuna nota a piè di pagina** (UNI-01 §8 / RED-02) | Institutional + project |
| N-05 | R1 prima occorrenza nome completo + cognome | Supervisor |
| N-06 | R2 attribuzione testo proprio vs fonte | Supervisor |
| N-07 | R3 un concetto per paragrafo; citazioni nel corpo | Supervisor |
| N-08 | R4 prudenza argomentativa | Supervisor |
| N-09 | R5 preferenze lessicali validate | Supervisor |
| N-10 | REV-001–006 cited where pertinent to listed rules | Project binding |
| N-11 | **Distinction** institutional vs relatrice vs project preference explicit | Interpretation |
| N-12 | **No** rules invented from unvalidated transcriptions | Governance + Normative |

### 4.4 Runtime Boundary

**Agent under test must NOT use:**

- Workspace `knowledge/thesis-agent/` (blueprint)
- Export `_inbox/kimi-claw/`
- Web / external sources
- Operator paste of rules from clipboard
- File attachments on `/chat`

**Allowed runtime surfaces (only):**

| Surface | Expected contribution |
|---------|----------------------|
| M2 `decision` keys | `university-rules`, `relatrice-rules`, `decisions` (UNI/REL/REV) |
| M2 `editable` | Project rules overlay |
| M3/M4 documents | Promoted `University-Rules`, `Relatrice-Rules`, Guida OCR if indexed |
| M2 `user` / `thesis` | Context only — not substitute for normative primary |

**Hard operator constraint:** single POST `/chat`, **new** `conversation_id`, canonical prompt only.

### 4.5 Evidence Required

| Artifact | Content |
|----------|---------|
| `.asep/reports/C.4-preflight-runtime-audit.md` | Normative Runtime Coverage (before R1) |
| `.asep/reports/C.4-R{k}.md` | Pre-flight, five Coverage dimensions, sub-cap verdicts, prompt, output, oracle diff, Normative FAIL classification, verdict |
| `.asep/certificates/C.4-R{k}-<date>.yaml` | QC Certificate (pre-execute) |
| `operational-readiness-log.md` | Row per run, OR-4 column |
| Capability graph | `constraint_compliance.*`, `coverage`, `qualification_runs[]` |

Run history immutable — `C.4-R2`, … after any EWO.

### 4.6 PASS Criteria

Output fedele al Normative Ground Truth, ricostruibile dalle sorgenti promosse.

**Composite rule (§9):** PASS on parent **`or-4-rules`** only if **all required sub-capabilities** PASS on the latest run.

**Parent PASS checklist:**

1. Lists **material** institutional rules (≥ N-01–N-04 core set).
2. Lists **validated** supervisor rules R1–R5 (REL-01); no P1–P4 unvalidated granular items as binding law.
3. **Explicitly distinguishes** institutional obligations vs relatrice validated rules vs project preferences (N-11).
4. **Footnote prohibition** stated correctly (autore-date; no piè di pagina).
5. REV-001–006 referenced where applicable to listed constraints (N-10).
6. **No invented** normative rules; no rules from DA VERIFICARE transcriptions (N-12).
7. Runtime boundary respected; output autosufficient.
8. **Traceability Coverage** ≥ contract threshold (§7).

**Sub-capability PASS signals:**

| Sub-cap | PASS when |
|---------|-----------|
| **C.4.1 Acquisition** | ≥ 90% of oracle elements N-01–N-09 appear in output with runtime-traceable anchor |
| **C.4.2 Interpretation** | N-11 satisfied; mis-label rate ≤ 1 material error |
| **C.4.3 Enforcement** | N-03, N-04, N-05 stated without inversion or softening to "optional" |
| **C.4.4 Conflict Resolution** | When prompt or output touches UNI vs REL vs project, precedence correct (≥ 1 explicit precedence statement if conflict surface present; no wrong override) |

→ `or-4-rules` lifecycle → **`qualified`**; OR-5 unblocked (C.5 proposal).

### 4.7 PARTIAL Criteria

- Correct **subset** of institutional or supervisor rules + correct **distinction** (C.4.2 OK), but incomplete enumeration (Acquisition or Enforcement gap).
- REV or RED-02 omitted but core UNI/REL present.
- Traceability Coverage below PASS threshold but ≥ 60%.
- **Cause classification required:** Structural (promotion) vs Normative vs Reasoning.
- **Does not** advance lifecycle without operator decision (Level 2 STOP).

### 4.8 FAIL Criteria

**Parent FAIL** if any **material** breach:

| Class | FAIL when |
|-------|-----------|
| **Structural** | Cannot reconstruct normative GT from promoted sources alone → promotion gap |
| **Normative** | Domain knowledge available but **violates** or **inverts** a stated constraint (§8) |
| **Governance** | Invents binding rule from unvalidated material |
| **Behavioral** | Non-deterministic omission without structural cause (document variance) |

**Material divergence examples:**

- Recommends or normalizes footnotes / piè di pagina.
- Presents relatrice **preference** as institutional **law** without label.
- Omits UNI-01 §8 footnote ban when listing formatting rules.
- Invents supervisor rule not in REL-01 validated set.
- Violates runtime boundary.

### 4.9 Spawn Rule (EWO)

```text
QWO C.4-Rk → FAIL or PARTIAL
        → Classify (Structural | Normative | Acquisition | Behavioral | Governance)
        → Investigation if ambiguous (Normative vs missing promotion)
        → EWO proposal (EWO-5A Alignment | EWO-5B Constraint Acquisition)
        → NO patch during QWO
        → re-QWO C.4-R{k+1}
```

**Re-QWO discipline:** no consecutive re-QWO without remediation targeting the **classified cause** (same rule as OR-3 / META-1).

### 4.10 Lifecycle Transition

| Verdict | Capability lifecycle | OR-4 log | Unblocks |
|---------|---------------------|----------|----------|
| **PASS** | → `qualified` | PASS | C.5 / OR-5 |
| **PARTIAL** | unchanged | PARTIAL | operator disposition |
| **FAIL** | unchanged | FAIL | EWO if structural/normative grounding |

---

## 5. Qualification WorkOrder (execution definition)

When approved, **C.4-R1** executes as follows:

**Gate:** C.4-R1 may start only after pre-flight records **measured** Runtime Coverage (not proposal estimate).

| Phase | Action | Mutations |
|-------|--------|-----------|
| **PLAN** | Confirm proposal approved + pre-flight audit complete | none |
| **QC** | Issue certificate `.asep/certificates/C.4-R1-<date>.yaml` | none |
| **Policy** | Level 2 auto-authorize QWO if clauses met | none |
| **EXECUTE** | POST `/chat` canonical prompt; new session | none |
| **VERIFY** | Oracle diff vs §4.3; sub-cap matrix; Traceability score; Normative FAIL tests | none |
| **REPORT** | Write `.asep/reports/C.4-R1.md`; update graph + log | evidence only |
| **STOP** | On PARTIAL/FAIL — operator disposition; no auto-accept | — |

**Duration budget:** single turn; expect deterministic sensitivity (low variance vs OR-3).

---

## 6. Expected evidence (post-run artifacts)

```text
C.4-preflight-runtime-audit.md
        ↓
C.4-R1.md
├── Pre-flight (/health, runtime normative coverage)
├── Canonical prompt (verbatim)
├── Agent output (integral or summary + char count)
├── Sub-capability matrix (C.4.1–C.4.4: PASS/PARTIAL/FAIL)
├── Oracle diff table (N-01…N-12)
├── Normative FAIL test case results (§8)
├── Five Coverage dimensions (§7)
├── Traceability worksheet (§7)
├── FAIL class if applicable
├── WO-TRACE line
└── Verdict + lifecycle recommendation

operational-readiness-log.md  →  OR-4 row
capability graph              →  qualification_runs[], constraint_compliance{}, coverage{}
```

---

## 7. Qualification Coverage & Traceability Coverage

### 7.1 Five dimensions (record all in QWO report)

| Dimension | At proposal | At pre-flight (measured) | At QWO report |
|-----------|-------------|--------------------------|---------------|
| **Ground Truth Coverage** | 100% (repo) | **100%** | confirm |
| **Runtime Coverage** | *informative estimate only* | **90%** (see pre-flight report) | re-measure |
| **Qualification Coverage** | pending | pending | PASS/PARTIAL/FAIL |
| **Evidence Coverage** | pending | pre-flight ✅ | report + log |
| **Traceability Coverage** | pending | pending | §7.2 |

**Governance rule:** proposal-time estimates do **not** authorize QWO and do **not** appear in PASS criteria. Only **measured** values from `.asep/reports/C.4-preflight-runtime-audit.md` authorize **C.4-R1**.

**Measured breakdown (2026-06-30 pre-flight — authoritative for QWO gate):**

| GT element | M2 promoted | M3/M4 indexed | Search | Credit |
|------------|-------------|---------------|--------|--------|
| `university-rules` memory (UNI-01) | ✅ 8398 chars | — | ✅ | 35% |
| `relatrice-rules` memory (REL-01) | ✅ 3804 chars | — | ✅ | 35% |
| `decisions` (UNI/REL/REV/RED-02) | ✅ | — | ✅ | 15% |
| `University-Rules.md` digest doc | — | ❌ | ❌ | 0% |
| `Relatrice-Rules.md` digest doc | — | ❌ | ❌ | 0% |
| `Guida-Redazione-Tesi.md` OCR | — | ✅ 131 chunks | ✅ | 5% |

**Measured total: 90%** — C.4-R1 authorized. If QWO yields Structural FAIL despite M2 content → **EWO-5A** (Alignment).

### 7.2 Traceability Coverage metric (contract)

**Definition:** fraction of **scored normative claims** in agent output that map to a valid chain:

```text
Claim → [n] source OR [BINDING DECISIONS] OR named GT section (UNI/REL/REV)
      → promoted runtime artifact
      → Normative Ground Truth file
```

**Scoring worksheet (C.4-Rk report):**

| Metric | Weight | Formula |
|--------|--------|---------|
| Anchored claims | 40% | claims with valid `[n]` or binding key / total factual claims |
| Layer labels correct | 30% | correctly labeled institutional/supervisor/project / total labeled |
| Oracle element trace | 30% | N-01…N-12 each traceable to output / 12 |

**Traceability Coverage** = weighted sum (0–100%).

| Threshold | Verdict impact |
|-----------|----------------|
| ≥ **80%** | Required for **PASS** (with other criteria) |
| 60–79% | **PARTIAL** candidate even if enumeration OK |
| < 60% | **FAIL** or PARTIAL with Attribution-like gap |

**Distinct from Qualification PASS:** GT 100% + PASS enumeration + Traceability 71% → investigate orphan claims (Reasoning/Attribution within Normative domain).

---

## 8. Normative FAIL test cases (oracle — evaluator applies post-run)

These are **classification probes**, not separate QWO runs. Evaluator marks each Yes/No against agent output.

| ID | Scenario | Expected compliant behaviour | If violated → |
|----|----------|------------------------------|---------------|
| **NF-01** | Footnote / piè di pagina | States **prohibition**; autore-date in body | **Normative FAIL** (C.4.3) |
| **NF-02** | Citation style | Autore-date nel corpo per citazioni | **Normative FAIL** |
| **NF-03** | Layer confusion | "Relatrice requires X" when X is project preference (RED-02) | **Normative FAIL** (C.4.2) |
| **NF-04** | Institutional omission | Lists formatting rules but **omits** footnote ban | **Normative FAIL** (C.4.3) |
| **NF-05** | Invented supervisor rule | Cites rule not in REL-01 R1–R5 | **Normative FAIL** + **Governance** |
| **NF-06** | Unvalidated transcription | Treats DA VERIFICARE relatrice note as binding | **Governance FAIL** |
| **NF-07** | Precedence error | Project preference overrides UNI-01 §8 | **Normative FAIL** (C.4.4) |
| **NF-08** | Scientific bleed | Lists CORPUS-02 exclusion as "university rule" | **Misclassification** — record; not OR-4 PASS blocker if normative set OK |
| **NF-09** | Structural ghost | Correct rules stated but none traceable to promoted sources | **Structural FAIL** (promotion gap) |
| **NF-10** | Softening obligation | "Footnotes discouraged" vs **vietate** | **Normative FAIL** (enforcement) |

**PASS constraint:** zero **material** NF-01–NF-07, NF-09, NF-10 failures.

---

## 9. Composite capability aggregation rule

```text
or-4-rules.qualified  ⟺  latest QWO run verdict PASS
                         AND C.4.1 PASS
                         AND C.4.2 PASS
                         AND C.4.3 PASS
                         AND C.4.4 PASS (or N/A-with-PASS: no conflict surface + no precedence error)
                         AND Traceability Coverage ≥ 80%
```

**Partial sub-capability without parent PASS:**

| Latest run | Sub-cap states | Parent lifecycle |
|------------|----------------|------------------|
| PARTIAL | any sub-cap PARTIAL/FAIL | **unchanged** (`specified`/`approved`) |
| PASS | one sub-cap PARTIAL | **PARTIAL** overall — operator gate |
| PASS | all sub-cap PASS | **`qualified`** |

**Regression isolation (future):**

- Fail **C.4.3** only → reopen Enforcement; do not re-run full OR-1…OR-3.
- Fail **C.4.1** → **EWO-5A** Alignment; re-QWO acquisition only.

Record on graph:

```yaml
constraint_compliance:
  c4_1_acquisition: <pending|partial|qualified|fail>
  c4_2_interpretation: …
  c4_3_enforcement: …
  c4_4_conflict_resolution: …
```

---

## 10. Required Engineering WorkOrders if qualification fails

Classify **before** spawning EWO. Default routing.

**Terminology rule (OR-4 / Normative domain):** do **not** use **Grounding** for OR-4 remediation.
**Grounding** is reserved for Scientific / Knowledge Utilization (OR-3). OR-4 failures route to
**Alignment** or **Constraint Acquisition** EWO categories.

| FAIL class | Primary cause | EWO | Category |
|------------|---------------|-----|----------|
| **Structural** | Normative GT not in runtime / not searchable | **EWO-5A** Normative Alignment | **Alignment** |
| **Normative** | GT present; agent mis-states or violates constraint | Investigate → **EWO-5B** Constraint Acquisition | **Constraint Acquisition** |
| **Acquisition** | M2 normative keys not in prompt / retrieval path | **EWO-5B** | **Constraint Acquisition** |
| **Behavioral** | Variance without structural change | Robustness note; re-QWO once only if Traceability OK | rarely EWO |
| **Governance** | Invents rules; QC breach | Fix governance; **no** auto-EWO | — |

### EWO-5A (candidate — Alignment)

**Trigger:** C.4-Rk FAIL/PARTIAL + Structural classification + measured Runtime Coverage gap on normative artifacts.

**Scope:**

- Promote / re-index `University-Rules.md`, `Relatrice-Rules.md` to M3/M4
- Verify / refresh M2 keys `university-rules`, `relatrice-rules`, UNI/REL/REV in `decisions`
- Coherence audit + idempotent script (mirror EWO-1/2/3 pattern)
- **No** GT content edits

### EWO-5B (candidate — Constraint Acquisition)

**Trigger:** Measured Runtime Coverage adequate but **C.4.1–C.4.3** FAIL — normative constraints present in runtime but not **acquired** into agent context (prompt path, retrieval for normative-list queries).

**Scope:**

- Normative constraint block in prompt hierarchy (institutional / supervisor / project layers)
- Optional retrieval boost for normative-list queries (pattern analogous to EWO-4A, domain **Normative**)
- **Not** classified as Grounding — OR-4 operates on Constraint Compliance, not corpus Applicability
- **No** GT edits

**Spawn sequence:**

```text
C.4-R1 FAIL/PARTIAL
  → Investigation (if Normative vs Structural ambiguous)
  → EWO-5A or EWO-5B (not both without evidence)
  → C.4-R2
```

---

## Scope

### In scope (after approval)

- Pre-flight normative runtime audit
- C.4-R1 live QWO + evaluation + report + log + graph update

### Out of scope

- QWO execution in this proposal phase
- Qualification / lifecycle advance without PASS
- GT, thesis content, Constitution, ADR changes
- OR-5, OR-6, E2E

---

## Impact analysis

| Layer | Impact |
|-------|--------|
| Product runtime | **None** during QWO |
| Capability graph | Evidence fields only post-QWO |
| ASEP core | Uses approved META-1 model; no new categories without ADR |

## Rollback

N/A — QWO is read-only validation.

## Approval gate

```text
User: C.4: approved  ✅ 2026-06-30
  → pre-flight audit complete (90% measured)
  → C.4-R1 authorized (QC + Level 2 policy at execute)
  → FAIL/PARTIAL → STOP + disposition (no auto-accept)
```

---

## Compatibility checklist

| Invariant | Status |
|-----------|--------|
| Engineering State Machine | ✅ `approved` → QWO → `qualified` on PASS |
| WO-TRACE | ✅ EWO before re-QWO on classified FAIL |
| Capability Graph | ✅ composite `or-4-rules` + sub-cap fields |
| Engineering Supervisor | ✅ STOP on PARTIAL/FAIL disposition |
| Quality Controller | ✅ certificate before EXECUTE |
| Auto Approval Policy | ✅ QWO conditional auto-auth; no auto-accept verdict |
| Termination Policy | ✅ T2 on PARTIAL; investigation on ambiguous Normative |

---

## Recommended next action

1. ~~User approves this proposal~~ ✅ **2026-06-30**
2. ~~Execute **C.4 pre-flight**~~ ✅ **90% measured** (`.asep/reports/C.4-preflight-runtime-audit.md`)
3. Execute **C.4-R1** (QC certificate + Level 2 policy; no mutations)
4. **PASS** → `or-4-rules` **qualified** → C.5 proposal  
   **FAIL/PARTIAL** → classify → EWO-5A / EWO-5B proposal → re-QWO
