# Qualification WorkOrder Proposal — QWO-PX2-001

> **Status:** ✅ **APPROVED & EXECUTED** — QWO-PX2-001-R1 PASS (2026-07-04).
>
> Program: `.asep/programs/thesisos-product-v2.yaml`  
> Spec: `docs/product/specs/px2-research-workspace-experience.md` §24  
> Template: `.asep/templates/qualification-work-order-template.md`

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | QWO-PX2-001 |
| **Type** | **QWO** (Qualification WorkOrder) — validation only |
| **Capability** | `px-2-research-workspace` |
| **Milestone** | PX-2 Research Workspace Experience |
| **Lifecycle transition** | `specified` → `qualified` (on PASS) |
| **First run id** | QWO-PX2-001-R1 |

---

## Objective

Demonstrate on the **live stack** that all five user-perceived capabilities
(PX-2.1…PX-2.5) are operational, PX-1 qualification surfaces are unchanged,
and OR-1…OR-7 regression remains green.

---

## Qualification Contract

### Capability Coverage (pre-flight — pending execution)

| Dimension | Value |
|-----------|-------|
| Ground Truth Coverage | Product spec §24 AC-1…AC-14 |
| Runtime Coverage | Live docker stack (`make up`) |
| Qualification Coverage | pending |
| Evidence Coverage | pending |

### Capability

`px-2-research-workspace` — PX-2 Research Workspace Experience.

### Prerequisiti

| Precondition | Expected state | Verification |
|--------------|----------------|--------------|
| PX-1 qualified | QWO-PX1-001-R1 PASS | Certificate on file |
| PX2-EWO-001…008 | All `implemented` | Reports in `.asep/reports/` |
| EXECUTION-AUTHORIZATION-PX2 | Amendment ratified | Sign-off in amendment doc |
| `make ci` | Green at QWO start | CI log in report |

### Ground Truth

| Priority | Artifact | Role |
|----------|----------|------|
| **Primary** | `docs/product/specs/px2-research-workspace-experience.md` §24 | Acceptance criteria |
| **Binding** | ADR-0036, ADR-0038, ADR-0039, ADR-0040 | IA + context + AI + state |
| **Regression** | QWO-PX1-001-R1 report | PX-1 surfaces unchanged |
| **Runtime** | OR-1…OR-7 qualification baseline | No regression |

### Runtime Boundary

**QWO operator (human or scripted walkthrough) uses:** live frontend + backend only.

**Must NOT regress:** OR-1…OR-7 behaviors verified in thesis-agent migration track.

**Allowed surfaces:** Context API, chapters API, writer actions, corpus retrieval,
memory proposal bundle, all PX-2 workspace routes.

### Evidence Required

| Artifact | Content |
|----------|---------|
| `.asep/reports/QWO-PX2-001-R1.md` | Pre-flight, AC checklist, screenshots/log refs, verdict |
| `.asep/certificates/QWO-PX2-001-R1-*.yaml` | QC certificate |
| Capability graph | `px-2-research-workspace` → `qualified` on PASS |

### PASS Criteria (from spec §24)

| # | Criterion | Capability |
|---|-----------|------------|
| AC-1 | ContextBar live counts match Context Packet for chapter + selection | PX-2.1 |
| AC-2 | Binding decision in Inspector when retrieval would contradict | PX-2.1 |
| AC-3 | Editor autosave + chapter switch without data loss | PX-2.2 |
| AC-4 | ≥4 AI actions with streaming from Writing panel | PX-2.2 |
| AC-5 | AI apply creates proposal — not silent write | PX-2.2 |
| AC-6 | Source picker → peek → cite inserts marker | PX-2.3 |
| AC-7 | Excluded source cite blocked with message | PX-2.3 |
| AC-8 | Decision card readable; frozen edit blocked | PX-2.4 |
| AC-9 | Continua restores chapter, section, panel tab | PX-2.5 |
| AC-10 | Session close atomic proposal bundle | PX-2.5 |
| AC-11 | Review accept/reject with operator confirm | PX-2.2 |
| AC-12 | Home progress updates on chapter status change | PX-2.5 |
| AC-13 | OR-1…OR-7 green; PX-1 surfaces unchanged | Regression |
| AC-14 | `make ci` green | Engineering gate |

**PASS:** All AC-1…AC-14 demonstrated with evidence.

### PARTIAL Criteria

Any AC failed with documented cause. No lifecycle advance without operator decision.
Supervisor **never** auto-accepts PARTIAL.

### FAIL Criteria

Material capability gap, PX-1 regression, OR regression, or `make ci` red.

### Spawn Rule

```text
QWO-PX2-001-Rk → FAIL/PARTIAL → EWO corrective proposal → re-QWO QWO-PX2-001-R{k+1}
```

### Lifecycle Transition

| Verdict | Capability | Unblocks |
|---------|------------|----------|
| PASS | `px-2-research-workspace` → `qualified` | PX-3 authorization gate |
| PARTIAL | unchanged | operator decision |
| FAIL | unchanged | corrective EWO |

---

## Scope

### In scope (after approval)

- Pre-flight environment declaration
- Live walkthrough AC-1…AC-14
- OR-1…OR-7 regression suite
- Report + certificate

### Out of scope

- Code mutation during QWO
- PX-3 features
- META-2 framework changes

---

## Test protocol

### Canonical walkthrough

```text
1. make up && make ci (baseline)
2. Home → Continua → verify AC-9 URL restoration
3. Writing → select text → 4 AI actions → Applica → verify AC-4, AC-5
4. ⌘⇧C cite flow → excluded source block → AC-6, AC-7
5. ContextBar + Inspector binding decision → AC-1, AC-2, AC-8
6. Session close bundle → AC-10
7. Review accept/reject → AC-11
8. Chapter status change → Home progress → AC-12
9. OR-1…OR-7 regression
10. PX-1 spot-check (sidebar, context v0, home default)
```

---

## Impact analysis / Rollback / Approval gate

No architecture impact. Rollback: revert to PX-1 qualified baseline.
**Explicit operator approval required** before QWO execution.

---

## Recommended next action

1. Ratify `EXECUTION-AUTHORIZATION-PX2-AMENDMENT`
2. Implement PX2-EWO-001…008
3. Operator approves this QWO proposal
4. Execute `QWO-PX2-001-R1`

---

## WO-TRACE

```text
PX2-EWO-001…008 → QWO-PX2-001-R1 → PX-2 QUALIFIED → PX-3 gate
```
