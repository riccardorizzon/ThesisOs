# Qualification WorkOrder Proposal — <ID>

> **Status:** ⏳ **Awaiting user approval** — no QWO execution authorized.
>
> Program: `.asep/programs/<program>.yaml`  
> Spec: `knowledge/thesis-agent/_migration/operational-readiness.md` § <OR-n | E2E>  
> Template: this file

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | <C.n | D.n> |
| **Type** | **QWO** (Qualification WorkOrder) — validation only |
| **Capability** | `<node-id>` |
| **Lifecycle transition** | `specified` → `approved` → `qualified` (on PASS) |
| **First run id** | `<ID>-R1` |

---

## Objective

<One paragraph: what capability is proven on the live system.>

---

## Qualification Contract

**Mandatory section.** Defines the binding agreement for execution and evaluation.

### Capability Coverage (observability)

Include a **pre-proposal or pre-flight** snapshot (see `docs/engineering-program.md` § Capability Coverage):

| Dimension | Value |
|-----------|-------|
| Ground Truth Coverage | … |
| Runtime Coverage | … |
| Qualification Coverage | pending / PASS / PARTIAL / FAIL |
| Evidence Coverage | … |

Update all four dimensions in the QWO report at conclusion.

**Availability vs Applicability vs Completeness** (when corpus or decision boundaries apply):
see `docs/engineering-program.md` § Capability Coverage.

### Capability

`<capability-id>` — <title>.

### Prerequisiti

| Precondition | Expected state | Verification |
|--------------|----------------|--------------|
| … | … | … |

### Ground Truth

| Priority | Artifact | Role |
|----------|----------|------|
| **Primary** | `<path>` | … |
| **Binding** | `Decisions.md` | … |

<List mandatory GT elements for PASS.>

### Runtime Boundary

**Agent under test must NOT use:** workspace files, inbox export, web, operator paste, attachments.

**Allowed runtime surfaces:** M2 memories, M3/M4 promoted documents, M6 chapters (list expected).

### Evidence Required

| Artifact | Content |
|----------|---------|
| `.asep/reports/<ID>-R{k}.md` | Pre-flight, Capability Coverage, prompt, output, oracle diff, verdict |
| `operational-readiness-log.md` | New row per run |
| Capability graph | `coverage` + `qualification_runs[]` |

Run history immutable — see `docs/engineering-program.md` § Qualification run instances.

### PASS Criteria

Numbered checklist — output fedele al Ground Truth, solo sorgenti promosse.

### PARTIAL Criteria

Correct subset + documented gaps + cause (agent vs promotion gap). No lifecycle advance without user decision.

### FAIL Criteria

Material divergence from GT, invented facts, boundary violation, promotion gap preventing reconstruction.

### Spawn Rule (eventuale EWO)

```text
QWO <ID>-Rk → FAIL/PARTIAL (promotion gap) → Evidence → EWO proposal → re-QWO <ID>-R{k+1}
```

Document **known promotion gaps** at proposal time if any.

### Lifecycle Transition

| Verdict | Capability | Log | Unblocks |
|---------|------------|-----|----------|
| PASS | → `qualified` | PASS | next capability |
| PARTIAL | unchanged | PARTIAL | user decision |
| FAIL | unchanged | FAIL | EWO if structural |

---

## Scope

### In scope (after approval)

- Pre-flight, live test, evaluation, report, log

### Out of scope

- Any mutation to knowledge, memory, documents, chapters, backend, frontend
- Corrective fixes during QWO

---

## Test protocol

### Canonical prompt

```text
<prompt from operational-readiness.md>
```

---

## Impact analysis / Rollback / Approval gate

<Standard QWO: no architecture impact; rollback N/A; explicit user approval required.>

---

## Recommended next action

1. User approves proposal  
2. Execute `<ID>-R1`  
3. PASS → next capability proposal; FAIL → EWO proposal if needed
