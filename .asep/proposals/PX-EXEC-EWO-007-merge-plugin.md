# Engineering WorkOrder Proposal — PX-EXEC-EWO-007

> **Status:** PROPOSED — dispatch authorized @ 2026-07-06; pending per-EWO develop authorization  
> **Prerequisites:** Wave A complete (EWO-001…006 **IMPLEMENTED**); MB2-Q4 **PASS** @ 2026-07-06

| Field | Value |
|-------|-------|
| **Program** | `.asep/programs/px-exec.yaml` |
| **Phase** | PX-EXEC-P2 — Execution Plugins |
| **SoR revision** | 2026-07-05 (read-only) |
| **Capability** | `px-exec-7-merge-plugin` |

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX-EXEC-EWO-007 |
| **Type** | **EWO** — Platform / Reference Implementation |
| **EWO category** | **Infrastructure** |
| **Milestone** | MB2 — Engineering Runtime |
| **Layer** | Runtime (Build Control Plane) |
| **Lifecycle transition** | `specified` → `implementing` (on develop authorization) → `done` (on PASS report) |

---

## Objective

Implement the **Merge Plugin** per SoR §8.2: `eligible(job)`, `execute(context)`,
`report()` — registered via Plugin Registry, driven by Rule Engine `merge` action
descriptors, enforcing `merge_order` from Program Graph (INV-R-03), emitting
`MergeCompleted` / `MergeFailed` events — **without** performing in-process git mutations
(Era I D8 / external integrator), **without** Integration or Qualification plugins, and
**without** claiming §13.3 golden path PASS or MB2 promotion.

This EWO enables live merge lifecycle events for Phase 2 golden path replay; it does
**not** re-qualify MB2-Q1 or MB2-Q4.

---

## SoR mapping

### Primary sections

| SoR § | Requirement | EWO-007 deliverable |
|-------|-------------|---------------------|
| **§8.2** merge interface | `eligible`, `execute`, `report` | `MergePlugin` class in `merge.py` |
| **§8.4** Plugin failure | Emit `MergeFailed` or escalate | Failure path + event emission |
| **§6.3** Events | `MergeCompleted`, `MergeFailed` | Bus publish on execute outcome |
| **§7.3** `post-ewo-merge` | Rule → merge action | Registry resolve + execute hook |
| **§4.2** merge_order | Dependency Engine ordering | `eligible()` consults graph merge_order |

### Traceability

| Req ID | Requirement | Gate | Test ID (future — not claimed now) |
|--------|-------------|------|-------------------------------------|
| REQ-04 | merge_order enforced | MB2-Q1 | MB2-Q-003 (live path extension) |
| REQ-10 | Plugin registry | MB2-Q4 | MB2-Q-010 (live merge registration) |
| REQ-16 | PX-2 golden path | §13.3 | MB2-Q-018 (partial — merge stage) |

### Invariants

| Invariant | EWO-007 enforcement |
|-----------|---------------------|
| **INV-R-03** | `eligible()` rejects out-of-order jobs vs Program Graph `merge_order` |
| **INV-R-08** | State changes via typed events only |
| **INV-R-14** | Core resolves merge via Registry — no direct import of merge impl outside registry bootstrap |
| **INV-R-04** | No in-process git merge — `execute()` emits events + merge manifest for external worker |

---

## Ownership (exclusive)

```text
builder_engine/merge.py                           # extend — MergePlugin + MergeContext + report types
builder_engine/tests/test_merge_plugin.py         # new — unit + merge_order tests
builder_engine/tests/fixtures/merge_order_graph.yaml  # new — INV-R-03 fixture
```

**Shared read-only:**

```text
builder_engine/plugin_registry.py   # register/resolve merge interface
builder_engine/rules.py             # ActionDescriptor; RuleEngine subscriber wiring
builder_engine/events.py            # MergeCompleted, MergeFailed publish
builder_engine/dependency.py        # merge_order / graph consultation
builder_engine/program_graph.py     # Program Graph merge_order fields
```

**Integration touch (minimal, documented in EWO report):**

```text
builder_engine/cycle.py             # optional: register MergePlugin factory at startup
```

---

## Forbidden paths

```text
backend/app/**
frontend/**
builder_engine/integration.py       # EWO-008
builder_engine/qualification.py     # EWO-009
docs/superpowers/specs/mb2-engineering-runtime-spec.md   # SoR — no edits
.asep/governance/**                 # no policy changes
```

**Behavioral exclusions:**

- In-process `git merge` / branch mutations
- Integration / QWO plugin execution (EWO-008, 009)
- MB2 promotion or §13.3 PASS claim
- Product milestone work (PX-4)

---

## Scope

### In scope

1. **`MergeContext` dataclass** — job_id, program_id, packet_ids, merge_order index, checkpoint
2. **`MergePlugin` class:**
   - `eligible(job_id, *, graph) -> MergeEligibility` — merge_order + dependency checks
   - `execute(context) -> MergeResult` — emit events; produce external-worker manifest (no git)
   - `report() -> MergeReport` — last execution summary
3. **Registry bootstrap** — factory registers as `merge` interface (api_version 1)
4. **Rule Engine hook** — on `merge` action descriptor, resolve + execute MergePlugin
5. **Event emission** — `MergeCompleted` / `MergeFailed` with normative payload fields
6. **Preserve Era I stub** — `merge_eligibility()` retained or delegated; existing callers unchanged
7. **Tests** — see Acceptance tests
8. **EWO completion report** — `.asep/reports/PX-EXEC-EWO-007-merge-plugin.md`

### Out of scope

- Integration plugin (EWO-008)
- Qualification plugin (EWO-009)
- Full PX-2 parallel automated replay (§13.3 bundle)
- AgentProvider dispatch (Phase 4)

---

## Acceptance criteria (EWO exit)

- [ ] MergePlugin satisfies §8.2 interface; registers via PluginRegistry
- [ ] `eligible()` enforces merge_order (INV-R-03) with fixture graph
- [ ] `execute()` emits `MergeCompleted` or `MergeFailed`; no silent failure (§8.4)
- [ ] No in-process git mutations; external integrator contract documented
- [ ] Rule Engine `post-ewo-merge` action triggers merge plugin in unit test
- [ ] Era I tests unchanged (`make unit-builder-engine` green)
- [ ] EWO report filed with traceability to §8.2, REQ-04, REQ-10
- [ ] **No §13.3 PASS or MB2 promotion claim** in EWO report

---

## Acceptance tests (design specification)

| Test ID | Description | SoR / INV |
|---------|-------------|-----------|
| `test_merge_plugin_registers` | Factory registers merge interface | §8.2, MB2-Q-010 |
| `test_merge_order_enforced` | Out-of-order job rejected | INV-R-03 |
| `test_merge_execute_emits_completed` | Success → MergeCompleted event | §6.3 |
| `test_merge_execute_emits_failed` | Failure → MergeFailed event | §8.4 |
| `test_no_git_mutation` | execute does not invoke git subprocess | Era I D8 |
| `test_rule_action_triggers_merge` | post-ewo-merge descriptor → plugin | §7.3 |
| `test_merge_report` | report() returns last outcome | §8.2 |

---

## Dependencies

| Depends on | Status |
|------------|--------|
| PX-EXEC-EWO-001…006 Wave A | **PASS** @ 2026-07-06 |
| MB2-Q4 Plugin Registry | **PASS** @ 2026-07-06 |
| Phase 2 dispatch authorization | **PASS** @ 2026-07-06 |
| Architect authorization for EWO-007 develop | **PENDING** |

**Unblocks:** PX-EXEC-EWO-008 Integration Plugin

---

## Exit criteria (WorkOrder complete)

| Criterion | Evidence |
|-----------|----------|
| Implementation on branch | `merge.py` + tests + fixtures |
| Verification green | `make unit-builder-engine` log in EWO report |
| Scope honored | No forbidden paths; no SoR diff |
| Traceability | EWO report maps deliverables → §8.2, REQ-04 |
| Downstream ready | MergeCompleted events available for EWO-008 |
| Qualification boundary | Report states: **does not satisfy §13.3** |

---

## WO-TRACE

```text
AUTHORIZE Phase 2 dispatch → EWO-007 proposal registered
  → AUTHORIZE PX-EXEC-EWO-007 → implement → verify → report PASS
  → unblocks EWO-008
```
