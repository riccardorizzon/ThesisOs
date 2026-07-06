# Engineering Program

> **META-0 binding.** This document defines how **ASEP** (how to evolve systems)
> governs **ThesisOS** (the system being evolved) without duplicating rules that
> already live in the Constitution, ADRs, plans, or domain runbooks.
>
> An Engineering Program is **above WorkOrders**. WorkOrders are instances; the
> Program is the long-lived contract for scope, roadmap, validation, and release.
>
> **Why invest in platform work?** See `docs/platform-justification.md` (hypotheses,
> exit criteria, Category A/B/C — not a duplicate of this doc).

---

## Architecture binding

### Engineering Platform (governance stack)

```text
ASEP                          (.asep/, skill asep)
  ↓
Engineering Supervisor        (state machine — orchestrates, does not implement)
  ↓
Quality Controller            (QC Certificate — attestation only)
  ↓
Engineering Program           (this doc + .asep/programs/*.yaml)
  ↓
Engineering State Machine     (allowed lifecycle transitions)
  ↓
Capability Graph              (.asep/capabilities/*.yaml)
  ↓
WorkOrders (EWO / QWO)
  ↓
Runtime                       (ThesisOS live stack)
  ↓
Product under evolution       (ThesisOS + domain blueprint)
```

This stack is **program-agnostic** — it can govern any document-engineering program,
not only ThesisOS.

### Domain track (thesis-agent migration)

```text
Engineering Program
        ↓
Thesis Agent Domain (knowledge/thesis-agent/)
        ↓
Migration Runbook
        ↓
Operational Readiness OR-1…OR-7
        ↓
End-to-End (E2E)
        ↓
Release Baseline
```

Legacy binding diagram (unchanged semantics):

```text
ASEP Platform (.asep/, skill asep)
        │  how to evolve (inner loop: WorkOrder → Execute → Qualify → Promote)
        ▼
Engineering Program (this doc + .asep/programs/*.yaml)
        │  which domain track, roadmap, completion criteria
        ▼
ThesisOS Product (backend/, frontend/, runtime Constitution)
        │  the runtime being validated
        ▼
Thesis Agent Domain (knowledge/thesis-agent/)
        │  blueprint + migration artifacts until release baseline
        ▼
Migration Runbook (docs/kimi-to-thesisos-migration-runbook.md)
        │  path for Kimi → ThesisOS knowledge migration
        ▼
Operational Readiness OR-1…OR-7
        │  capability-level done (live agent, not file existence)
        ▼
End-to-End (E2E)
        │  session-level integration done
        ▼
Release Baseline
        commit + frozen logs + ThesisOS operativo
```

**Single source of truth (no duplication):**

| Concern | Authoritative artifact |
|---------|------------------------|
| Platform invariants | `docs/runtime-constitution.md` |
| Layer / event rules | `decisions/ADR-0030-agent-runtime-layer-boundaries.md` |
| ASEP pipeline stages | `.asep/pipeline/*`, `.asep/resolvers/*` |
| Runtime milestone scope | `plans/*.md` + `.asep/capabilities/runtime-platform.yaml` |
| Thesis-agent migration path | `docs/kimi-to-thesisos-migration-runbook.md` |
| OR / E2E test specs | `knowledge/thesis-agent/_migration/operational-readiness.md` |
| OR / E2E execution log | `knowledge/thesis-agent/_migration/operational-readiness-log.md` |
| Domain decisions | `knowledge/thesis-agent/03_PROJECT/Decisions.md` |
| Active program instance | `.asep/programs/thesis-agent-migration.yaml` |
| Capability navigation (migration track) | `.asep/capabilities/thesis-agent-migration.yaml` |
| Auto-approval (Level 2 default) | `docs/auto-approval-policy.md` |
| Quality Controller checklist | `.asep/governance/quality-controller.md` |
| Engineering Supervisor role | `.asep/governance/engineering-supervisor.md` |
| QC Certificate template | `.asep/governance/qc-certificate-template.md` |
| Termination Policy | `docs/termination-policy.md` |
| Stop Report template | `.asep/governance/stop-report-template.md` |
| Investigation reports | `.asep/reports/*-investigation.md` (read-only, pre-EWO) |
| Capability model (domains, sub-capabilities, traceability) | `docs/asep-capability-model.md` |

---

## Outer loop (program evolution)

Manages **what** to do next. Runs when spawning or reprioritizing WorkOrders.

```text
Observe Repository
        → HEAD, branch, reports, program yaml, capability lifecycle states
Update Roadmap
        → sync .asep/programs/* and capability graph status/lifecycle
Prioritize Capability
        → first node with lifecycle ≤ approved AND status = ready
Spawn WorkOrder
        → .asep/templates/work-order-template.md scoped to that capability
```

Operator surface: `ASEP: continua` with program context, explicit capability
(`ASEP: esegui OR-1 thesis-agent`), or **Architect authorization** (`AUTHORIZE PX-3`).

---

## Architect Authorization API

Stable high-level interface between the **Architect (operator)** and ASEP. One command
replaces long briefing prompts; governance history lives in rules and docs.

### Command

```text
AUTHORIZE PX-3
AUTHORIZE PROGRAM PX-3
ASEP: AUTHORIZE PX-3
```

Structured blocks (`# ARCHITECT AUTHORIZATION` + `Status: AUTHORIZED`) resolve to the
same intent. Resolver: `.asep/resolvers/authorize.md`.

### Interpretation (today: skill + agent; future: Engineering Runtime)

```text
1. Load Program Graph          (.asep/programs/*.yaml)
2. Pre-flight validation       (deps, repo, SoR for conformance programs)
3. Select first executable EWO (dependency order)
4. Record authorization receipt (.asep/reports/<PROGRAM>-AUTHORIZATION-<date>.md)
5. Enter develop pipeline      (scoped to authorized EWO)
6. Conformance programs        → product code only; I/S/A/N log
```

The command **is** explicit authorization. It supersedes program-level blocks such as
`excluded_until_gate_3_amendment` when issued by the Architect.

**Do not** on authorize: modify Governance, edit SoR, implement Engineering Runtime,
or redesign architecture.

### Program roles

| Role | Example | Constraints |
|------|---------|-------------|
| **engineering** | PX-1, PX-2, thesis-agent OR/E2E | Standard ASEP develop + QC |
| **conformance** | PX-3+ under MB2 SoR | Product-only; SoR read-only; `.cursor/rules/px3-conformance-program.mdc` |

Interface stability: the Architect command does not change when execution moves from
agent interpretation to automated Engineering Runtime.

---

## Inner loop (WorkOrder execution)

Manages **how** a single capability is delivered. Identical to ASEP today:

```text
Discovery → Impact Analysis → Proposal → Approval → Implementation
        → Qualification → Promotion → Freeze → Report
```

Mapped to `.asep/pipeline/executor.md`, `qualification.md`, `promotion.md`.

### Human gate vs automation

**Approval is a control gate, not a technical step.** The program supports three
automation levels — see `docs/auto-approval-policy.md`:

| Level | Model |
|-------|--------|
| **1** | Auto-loop with human gate at every proposal (safest) |
| **2** | **Conditional auto-approval** — QC + policy; human on STOP triggers (**default**) |
| **3** | Autonomous loop — QC PASS → auto-approve; human on QC FAIL |

**Default (Level 2):** After **QC Certificate PASS**, Supervisor may auto-authorize
low-risk WorkOrders per policy — **not** QWO unless all **QWO auto-authorization** clauses
hold (approved proposal, no pending EWO, no open STOP, GT unchanged).

**Always human:** Ground Truth edits, new decisions, Constitution/ADR changes, architecture
changes, new capabilities, release baseline, **QWO PARTIAL/FAIL disposition** (Outer Loop).

```text
PLAN → QC issues Certificate → Supervisor reads → Policy + Termination → EXECUTE | WAIT
```

Components: `.asep/governance/quality-controller.md`,
`.asep/governance/qc-certificate-template.md`, `.asep/governance/engineering-supervisor.md`,
`docs/termination-policy.md`.

Legacy rule preserved: **no implementation without authorization** — authorization may be
explicit operator approval **or** documented auto-approval under policy.

---

## WorkOrder types

| Type | Abbr. | Mutates system | Lifecycle step | Template |
|------|-------|----------------|----------------|----------|
| **Engineering WorkOrder** | EWO | Yes — code, docs, memory, runtime, architecture | `implemented` (and beyond) | `.asep/templates/work-order-template.md` |
| **Qualification WorkOrder** | QWO | No — evidence, logs, lifecycle advance only | `specified` → `approved` → `qualified` | `.asep/templates/qualification-work-order-template.md` |

### EWO categories (taxonomy — does not change lifecycle)

Classifies **engineering intent** for backlog analysis. Optional field on every EWO proposal:
`ewo_category`.

| Category | Meaning | Migration track examples |
|----------|---------|--------------------------|
| **Alignment** | Ground Truth → promoted runtime surfaces (knowledge/memory/docs) | EWO-1 (outline), EWO-2 (STIGMATA methodology), EWO-3 (corpus masters) |
| **Grounding** | Cognitive context pipeline — binding decisions, prompt hierarchy, retrieval glue | EWO-4 (exclusions), **EWO-4A** (corpus-list retrieval) |
| **Promotion** | Bulk or phase ingest of domain artifacts to runtime | Fase B (`promote_runtime.py`) |
| **Refactoring** | Restructure artifacts/code without changing GT semantics | — |
| **Normalization** | Converge duplicates, naming, schema drift | — |
| **Infrastructure** | Platform, scripts, CI, observability | META-0 binding |
| **Release** | Baseline freeze, commit, program completion | E.1 |

Categories are **orthogonal** to capability lifecycle (`draft` … `frozen`). An Alignment EWO
still transitions `approved` → `implemented` on success; category only aids Outer Loop triage.

- **EWO** examples: META-0 (Infrastructure), Fase B (Promotion), EWO-1/2/3 (Alignment), **EWO-4 (Grounding)**, release (Release).

### Cognitive pipeline (Ground Truth → Response)

Four responsibilities — classify failures and EWO category:

```text
Ground Truth  →  Retrieval  →  Grounding  →  Reasoning  →  Response
     │               │              │              │
  repo/GT         search         prompt         model
  frozen          top-k          hierarchy      synthesis
```

| Level | Symptom | Typical fix |
|-------|---------|-------------|
| **Ground Truth** | Document missing in repo | Migrate / author GT |
| **Retrieval** | Document not returned by search | Index, query, ranking |
| **Grounding** | Retrieved / stored but not applied in prompt | **Grounding EWO** (EWO-4 class) |
| **Reasoning** | Context present; wrong synthesis | Robustness protocol; rarely EWO |

**Alignment** EWOs fix Ground Truth→runtime **promotion**. **Grounding** EWOs fix **Retrieval→Grounding→Reasoning** glue without GT edits.

Canonical Grounding instance: `.asep/reports/C.3-R2-investigation.md` → EWO-4.
- **QWO** examples: OR-1…OR-7, E2E session — proposals in `.asep/proposals/C.*.md`.

QWO execution **never** skips the proposal + approval step. Qualification uses
operational criteria (`operational-readiness.md` + approved `.asep/proposals/*.md`),
not `make ci` alone.

Proposals live in `.asep/proposals/`. Execution requires **authorization**:

- **Explicit:** operator approval (`EWO-n: approved`, `C.n-Rk: approved`, …)
- **Policy:** Level 2 — Supervisor reads **QC Certificate** + applies policy + termination rules

QWO **runs** may be auto-authorized only under **QWO auto-authorization** in
`docs/auto-approval-policy.md`. QWO **verdict acceptance** remains Outer Loop human gate.

**Runtime Knowledge Alignment (EWO pattern):** when a QWO FAILs due to promotion gap,
spawn an EWO to align Ground Truth → runtime surfaces, then re-QWO. Template instance:
`.asep/proposals/EWO-1-runtime-knowledge-alignment.md`.

### QWO discipline (non-negotiable)

Un **Qualification WorkOrder non corregge mai il sistema.**

Può esclusivamente:

1. **Qualificare** una capability (lifecycle → `qualified` on PASS)
2. **Produrre evidenze** (log, report)
3. **Aprire un EWO** se emerge un gap strutturale — mai patch durante il QWO

```text
QWO → FAIL → Evidence → EWO (fix promotion/architecture) → QWO (re-run) → PASS
```

Un test **non** diventa una fase di sviluppo. Separazione costruzione (EWO) vs
verifica (QWO) è obbligatoria.

**Re-QWO rule:** ogni re-QWO (`C.n-R{k+1}`) deve essere preceduto da un EWO (o
remediation documentata) che affronta la **causa** del run precedente non
soddisfacente. Re-QWO consecutivi senza cambiamento misurano solo varianza.

### QWO sensitivity classes

Not all QWOs tolerate the same run-to-run variance. Tag each capability QWO in its
proposal (`qwo_sensitivity`):

| Class | Characteristics | Examples | Expectation |
|-------|-----------------|----------|-------------|
| **Deterministic** | Stable across consecutive runs when runtime is aligned | OR-1 structure, OR-2 STIGMATA | Re-QWO after Alignment EWO usually sufficient |
| **Retrieval-sensitive** | Outcome depends heavily on ranking and top-k context | **OR-3 corpus** | Grounding remediation on retrieval **before** blind re-QWO |
| **Reasoning-sensitive** | Outcome depends on multi-source synthesis | OR-6 write paragraph | Robustness protocol; higher PARTIAL tolerance only if contract allows |

OR-3 is **Retrieval-sensitive**. EWO-4 / EWO-4A (Grounding) precede C.3-R4 by design.

### FAIL taxonomy (Outer Loop routing)

Not all FAIL/PARTIAL outcomes share the same remediation. Classify before spawning EWO:

```text
FAIL / PARTIAL (structural)

├── Structural
│     promotion gap — GT exists, runtime lacks artifact
│     → EWO Alignment
│
├── Runtime / Grounding
│     retrieval / ranking / prompt-path / binding-decision gaps
│     → EWO **Grounding** (EWO-4 class) or Infrastructure for pure index/ranking
│
├── Behavioral
│     reasoning / model variance — availability OK, synthesis inconsistent
│     → robustness protocol; optional Grounding tweak; rarely Alignment
│
├── Normative
│     domain knowledge OK but operational rule / policy / style constraint violated
│     → Alignment (missing normative GT) or Constraint Enforcement; see OR-4 model
│     → NOT corpus Grounding; NOT pure Reasoning
│
└── Governance
      policy / QC / invariant violation
      → fix governance; never auto-spawn EWO
```

**Investigation gate:** on ambiguous FAIL (e.g. Applicability regression with Runtime
Coverage ~100%), run read-only investigation (`.asep/reports/<run>-investigation.md`)
before EWO proposal. Operator disposition: `C.n-Rk FAIL: INVESTIGATE`.

Cause classes for investigation reports:

| Class | Meaning |
|-------|---------|
| Promotion Gap | GT not promoted |
| Retrieval Gap | content not returned by search |
| Ranking Gap | content exists but not in top-k for query |
| Grounding Gap | prompt rules suppress valid memory/decisions |
| Reasoning Gap | context present; model fails synthesis |
| Model Variance | non-deterministic run-to-run without structural change |
| Normative Violation | rule/policy known or promotable but not applied in output |

Canonical instance: `.asep/reports/C.3-R2-investigation.md` → **Grounding Gap** (primary).

**Knowledge domains & sub-capabilities:** `docs/asep-capability-model.md` (META-1).
OR-3 = Scientific / Knowledge Utilization; OR-4 = Normative / Constraint Compliance.

### Qualification run instances (re-QWO after EWO)

Each QWO execution is a **new qualification instance**, not a silent retry. Prior runs
remain in the audit trail.

| Convention | Example | Report path |
|------------|---------|-------------|
| **Run id** | `C.1-R1`, `C.1-R2`, `C.1-R3` | `.asep/reports/C.1-R{n}.md` |
| **Run number** | Run #1, Run #2, … | Header in each report |

Rules:

1. A new run after an EWO (or any re-qualification) gets the **next** run id — never overwrites the prior report file.
2. Capability `last_verdict` / `last_report` reflect the **latest** run; `qualification_runs[]` (or report cross-links) preserve history.
3. Lifecycle advances only on the **latest** PASS (or accepted PARTIAL); a historical FAIL remains valid evidence.

First migration-track instance: `C.1-R1` (legacy filename `C.1-or-1.md` retained for links).

### Qualification Contract (QWO proposals)

Every QWO proposal (C.2 … C.7, D.1 E2E) **must** include a fixed section:

**Qualification Contract** with subsections:

- Capability
- Prerequisiti
- Ground Truth
- Runtime Boundary
- Evidence Required
- PASS Criteria
- PARTIAL Criteria
- FAIL Criteria
- Spawn Rule (eventuale EWO)
- Lifecycle Transition

Template: `.asep/templates/qualification-work-order-template.md`  
Canonical example: `.asep/proposals/C.2-or-2-stigmata-framework.md`

C.1 predates this section (contract implicit in proposal body); do not rewrite historical reports.

### Qualification history (immutable)

La cronologia delle Qualification Run è **parte integrante** della capability e **non viene mai riscritta**.
Capability graph field: `qualification_runs[]`. Report files: `C.{n}-R{k}.md`.

**Structure Resolution Rule** (OR-1 e analoghi): il test non hardcoda il numero di
capitoli; confronta output runtime vs Ground Truth (outline congelato approvato).
Vedi `.asep/proposals/C.1-or-1-thesis-structure.md`.

---

## Capability lifecycle

Every capability in a Program traverses these states. **Lifecycle ≠ file exists.**

| State | Meaning | Typical evidence |
|-------|---------|------------------|
| `draft` | Intent only | discussion, no spec |
| `specified` | Testable spec exists | section in `operational-readiness.md`, plan, ADR |
| `approved` | Human accepted spec | user gate (e.g. UNI-01, REL-01) |
| `implemented` | Artifacts exist | code, promoted runtime, markdown materialized |
| `qualified` | Gates pass on live system | OR-n PASS in `operational-readiness-log.md` |
| `operational` | Integration proven | E2E PASS |
| `frozen` | Release baseline | commit, promotion log, no pending decisions |

ASEP `status` field (`done` \| `ready` \| `planned` \| `blocked`) is **navigation**;
`lifecycle` is **maturity**. Both appear in `.asep/capabilities/*.yaml`.

### Platform track lifecycle (MB2 / Engineering Runtime)

Platform capabilities (`.asep/capabilities/px-exec.yaml`, milestone **MB2**) use a
**separate lifecycle vocabulary** from the migration/product track:

| State | Meaning | Typical evidence |
|-------|---------|------------------|
| `proposed` | Intent; not yet normative | discussion, draft ADR |
| `specified` | **Specification of Record frozen** | SoR + Architect sign-off certificate |
| `implementing` | Reference Implementation in progress | code in `builder_engine/`, MB2-Q partial |
| `qualified` | Qualification gates PASS | MB2-Q1…Q6 Qualification Package |
| `promoted` | Platform milestone complete | tag `mb2-complete`, gate doc |
| `maintenance` | Accepting compatible SoR revisions | per `sor-compatibility-policy.md` |
| `deprecated` | Superseded by newer SoR / ADR | migration note |

**MB2 today:** `lifecycle: specified` — **not** `implementing`.

### Specification freeze vs implementation freeze

| Dimension | Product (e.g. PX-2) | Platform (MB2) |
|-----------|---------------------|----------------|
| Specification | Frozen (product spec) | **Frozen** (SoR — 2026-07-05) |
| Implementation | **Frozen** (qualified baseline) | **Open** (not authorized) |

Product milestones freeze **code**. Platform milestones freeze the **contract** first;
Reference Implementation follows Qualification gates.

Certificate: `.asep/certificates/MB2-SOR-20260705.yaml`  
Report: `.asep/reports/MB2-SPECIFICATION-FREEZE.md`  
Compatibility: `.asep/governance/sor-compatibility-policy.md`

---

## Engineering State Machine

The **Capability Lifecycle** describes **where** a capability is.  
The **Engineering State Machine** describes **how** it may move — which transitions are
allowed and which WorkOrder type enables each edge.

```text
                    ┌──────────────────────────────────────┐
                    │              QWO (C.n-Rk)              │
                    │                                      │
 draft ──► specified ──► approved ──────────────────────────┤
                    │         │              │             │
                    │         │         PASS │             │
                    │         │              ▼             │
                    │         │         qualified          │
                    │         │                            │
                    │         ├── PARTIAL ──► Outer Loop     │
                    │         │              │             │
                    │         ├── FAIL ──────┤             │
                    │         │              ▼             │
                    │         │         EWO (Alignment…)   │
                    │         │              │             │
                    │         │              ▼             │
                    │         │         implemented        │
                    │         │         (runtime aligned)  │
                    │         │              │             │
                    │         └──────────────┴──► re-QWO ───┘
                    │
                    └── (EWO may also originate from approved + gap evidence)
```

### Transition rules (non-negotiable)

| From | To | Enabled by | Notes |
|------|-----|------------|-------|
| `draft` | `specified` | Spec / proposal authoring | Human gate |
| `specified` | `approved` | User approves QWO or EWO proposal | No execution before approval |
| `approved` | `qualified` | **QWO PASS** or **QWO PASS\*** (operator disposition) | OR-n / E2E qualification |
| `approved` | unchanged | QWO PARTIAL or FAIL (without PASS\* disposition) | Evidence recorded; history preserved |
| gap evidenced | `implemented` | **EWO** success | Alignment / Promotion / … — not QWO |
| `implemented` | `qualified` | **re-QWO PASS** | New run id (C.n-R{k+1}) |
| `qualified` | `operational` | E2E PASS | Integration gate |
| `operational` | `frozen` | Release EWO (E.1) | Baseline commit |

**Forbidden transitions:**

- QWO → `implemented` (QWO never mutates system)
- EWO → `qualified` (EWO never self-qualifies; re-QWO required)
- PASS on re-QWO **without** overwriting prior FAIL/PARTIAL reports
- **Implicit lifecycle changes** (see invariant below)

### Invariant: deterministic transitions (WO-TRACE)

> Ogni transizione di lifecycle deve essere causata da **un singolo WorkOrder concluso**.
> Non sono ammesse transizioni implicite.

Ogni cambiamento di `lifecycle` nel capability graph deve essere tracciabile a:

| Required trace | Artifact |
|----------------|----------|
| **WorkOrder** | id + type (EWO \| QWO) — e.g. `C.2-R2`, `EWO-2` |
| **Report** | `.asep/reports/<WO-id-or-run>.md` |
| **Verdict** | PASS \| PASS\* \| PARTIAL \| FAIL (QWO) or internal validation PASS (EWO) |

Rules:

1. One WorkOrder conclusion → at most one lifecycle edge on the affected capability.
2. Manual edits to `lifecycle` in the capability graph **without** a matching report are forbidden.
3. `qualification_runs[]` and EWO `report:` fields are the audit chain — never delete prior entries.
4. Observing the capability graph + reports must fully reconstruct **why** the capability is in its current state.

Examples (migration track):

| Transition | WorkOrder | Report | Verdict |
|------------|-----------|--------|---------|
| `or-1` → `qualified` | C.1-R2 | `C.1-R2.md` | PASS |
| `ewo-2` → `implemented` | EWO-2 | `EWO-2-runtime-methodology-alignment.md` | PASS (internal) |
| `ewo-3` → `implemented` | EWO-3 | `EWO-3-runtime-corpus-alignment.md` | PASS (internal) |
| `ewo-4` → `implemented` | EWO-4 | `EWO-4-runtime-grounding-alignment.md` | PASS (internal) |
| `or-2` → `qualified` | C.2-R2 | `C.2-R2.md` | PASS |

### WorkOrder ↔ state mapping

| WorkOrder | Mutates runtime | Advances lifecycle to |
|-----------|-----------------|------------------------|
| **EWO** | Yes | `implemented` (on success) |
| **QWO** | No | `qualified` (on PASS or PASS\* only) |

Migration track instances:

| Capability | EWO (→ implemented) | QWO (→ qualified) |
|------------|---------------------|-------------------|
| OR-1 structure | EWO-1 Alignment | C.1-R1 FAIL, C.1-R2 PASS |
| OR-2 STIGMATA | EWO-2 Alignment | C.2-R1 PARTIAL, C.2-R2 PASS |
| OR-3 corpus | EWO-3 Alignment + EWO-4/4A Grounding | C.3-R1…R4 → **qualified** |
| OR-4 constraints | Alignment (normative promotion) | C.4 pending — **META-1 gate** |

---

## Capability Coverage

Observability layer — **complements** QWO verdict; does **not** replace PASS/PARTIAL/FAIL
or WO-TRACE. Recorded on capability graph and in QWO/EWO reports at pre-flight and post-run.

### Dimensions

| Dimension | Meaning | Typical measurement |
|-----------|---------|---------------------|
| **Ground Truth Coverage** | GT artifacts for this capability exist and are frozen in repo blueprint | % of required GT files/sections present in `03_PROJECT/` (or domain path) |
| **Runtime Coverage** | GT retrievable from promoted runtime **without workspace** | Weighted % of GT elements **promoted + indexed + search-from-artifact** |

**Do not conflate:**

| Observation | Counts toward |
|-------------|----------------|
| `.md` file exists in repo | **Ground Truth Coverage** only |
| Document uploaded + indexed in M3/M4 | Runtime promotion |
| `/search` hit from a *different* document mentioning similar keywords | **Not** coverage of the target GT artifact |
| Agent answers from book OCR without master index | Partial chat capability — measure in QWO, not as master coverage |

### Availability vs Applicability vs Completeness

QWO capabilities that depend on **corpus boundaries** (OR-3, bibliography discipline, writing,
revision, E2E) must distinguish three retrieval qualities (cumulative):

```text
Availability  →  Applicability  →  Completeness
```

| Term | Meaning | Example (OR-3) |
|------|---------|----------------|
| **Availability** | Runtime can retrieve information from a promoted source | `Barthes_Mythologies.md` indexed and searchable |
| **Applicability** | Runtime knows whether that information is **admitted**, **excluded**, or **contextual** for the capability under test | Mythologies **available** but **not applicable** to active corpus (CORPUS-02) |
| **Completeness** | Runtime reconstructs the **full set** required by Ground Truth without omissions or misclassification | All ~12 authors with role + chapter mapping from promoted masters |

**Rules:**

1. **Availability alone does not satisfy OR-n** when the Qualification Contract tests corpus
   boundaries or frozen decisions.
2. A QWO **PASS** on applicability requires the agent to apply GT constraints — e.g. exclude
   Mythologies from the active list while optionally noting Barthes via *Il sistema della moda*.
3. **PARTIAL** often means Applicability OK but Completeness insufficient (promotion gap or
   synthesis gap) — record all three dimensions in QWO reports.
4. Conflicting runtime signals (promoted OCR of an excluded work) are **expected** until
   Alignment EWOs normalize metadata; evaluate **Applicability**, not mere retrieval.
5. Record Availability / Applicability / Completeness in QWO reports when corpus boundaries apply.

Pre-flight OR-n should run **Repository Audit → Runtime Audit → Coverage Update → QWO** when coverage is uncertain.
| **Qualification Coverage** | Degree to which live QWO satisfied the Qualification Contract | **PASS** → 100%; **PARTIAL** → label + optional % in report; **FAIL** → 0% or gap score; *pending* before run |
| **Evidence Coverage** | Audit trail complete for latest concluded WorkOrder | 100% if report + log + run id + verdict; else partial |
| **Traceability Coverage** | Each response claim mappable through retrieval to GT (chain integrity) | 0–100% optional score in QWO report; see `docs/asep-capability-model.md` |

**Traceability** is orthogonal to Qualification PASS: a run may PASS contract checks
while Traceability < 100% (e.g. orphan claims, missing opera attribution). Record when
assessed; targets Attribution / Reasoning sub-capabilities under Knowledge Utilization.

### Rules

1. Updated at **proposal** (estimate), **QWO pre-flight**, **QWO report**, **EWO report**.
2. Does not advance lifecycle — only **QWO verdict** + WO-TRACE do.
3. Enables comparison across capabilities (OR-3 … OR-7, E2E) before commit to re-QWO/EWO.
4. Stored in `.asep/capabilities/*.yaml` under `coverage:` per capability node.

### Example snapshots

**OR-2 before EWO-2 (C.2-R1 accepted):**

```text
Ground Truth Coverage:    100%
Runtime Coverage:         ~72%
Qualification Coverage:   PARTIAL
Evidence Coverage:        100%
```

**OR-2 after C.2-R2 PASS:**

```text
Ground Truth Coverage:    100%
Runtime Coverage:         100%
Qualification Coverage:   100%
Evidence Coverage:        100%
```

**OR-3 after C.3-R1 PARTIAL (accepted):**

```text
Ground Truth Coverage:    100%
Runtime Coverage:         40%
Qualification Coverage:   PARTIAL (~45%)
Evidence Coverage:        100%
Availability:             partial
Applicability:            correct (CORPUS-02/03)
Completeness:             insufficient
```

**OR-3 after EWO-3 (pre C.3-R2):**

```text
Ground Truth Coverage:    100%
Runtime Coverage:         ~100%
Qualification Coverage:   PARTIAL (pending re-QWO)
Evidence Coverage:        100%
```

Prior estimate ~58% **superseded** at pre-flight — masters now promoted.

---

## Program structure (template)

Each `.asep/programs/<id>.yaml` may define:

| Section | Role |
|---------|------|
| `scope` | What this program delivers |
| `architecture_binding` | Pointers (paths only) |
| `capability_graph` | Which yaml graph to load |
| `workorder_backlog` | Ordered WorkOrder ids → capability nodes |
| `validation_rules` | Pointer to OR/E2E or `qualification.md` |
| `promotion_rules` | Pointer to runbook / `promotion.md` |
| `completion_criteria` | Program-level done |

---

## Active programs

| Program | Id | Status |
|---------|-----|--------|
| Thesis Agent Migration (Kimi → ThesisOS) | `thesis-agent-migration` | **active** — see `.asep/programs/thesis-agent-migration.yaml` |
| Runtime Platform (M5/M6…) | *(implicit via plans)* | governed by `runtime-platform.yaml` + milestone plans |

When a request touches **thesis-agent**, **OR-**, **E2E**, or **migration**, load the
**thesis-agent-migration** program and graph before resolving capability (see
`.asep/resolvers/capability.md`).

---

## Completion (migration program)

The migration program ends **only** when:

- All capabilities in `.asep/capabilities/thesis-agent-migration.yaml` are `lifecycle: frozen`
- OR-1…OR-7 **PASS** on live agent (`operational-readiness-log.md`)
- E2E **PASS** (same log)
- Repository consistent; no orphan docs; no pending domain decisions blocking release
- Release baseline committed (text first; binaries per runbook)

Until then, ThesisOS evolution on this track proceeds **one WorkOrder per capability** —
never a mega-prompt.
