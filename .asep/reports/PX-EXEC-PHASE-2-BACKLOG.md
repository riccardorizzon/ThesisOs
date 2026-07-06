# PX-EXEC Phase 2 — Backlog Definition

> **Authority:** Architect (operator-authorized dispatch)  
> **Date:** 2026-07-06  
> **Status:** **REGISTERED** — dispatch authorized  
> **Program:** `.asep/programs/px-exec.yaml`  
> **Phase:** PX-EXEC-P2 — Execution Plugins  
> **SoR revision:** 2026-07-05 (read-only)  
> **Authorization:** `.asep/reports/PX-EXEC-AUTHORIZATION-PHASE-2-DISPATCH-20260706.md`

---

## Functional objective (PX-EXEC Phase 2)

Register **Merge**, **Integration**, and **Qualification** engines as Runtime plugins
driven by Rule Engine action descriptors — replacing manual `orchestrate-builders` steps
for wave lifecycle (merge order, integration review, QWO spawn).

**Platform thesis** (ADR-0042 §5, SoR §8):

```text
Rule Engine action descriptor  →  Plugin Registry.resolve  →  Plugin.execute
```

Phase 2 implements plugin **interfaces** and event emission. It does **not** mutate the
Product Plane, does **not** perform git merge in-process (external integrator per Era I D8),
and does **not** claim MB2 promotion or §13.3 golden path PASS until EWO-007…009 complete
and replay evidence is filed.

---

## Authoritative sources (not agent-invented)

| Artifact | Role |
|----------|------|
| `docs/superpowers/specs/mb2-engineering-runtime-spec.md` | SoR §7.3, §8.2, §13.3 (normative) |
| `docs/platform/runtime-model-v2.md` | §7 plugin lifecycle |
| `decisions/ADR-0042-engineering-runtime.md` | Plugin registry, event-driven execution |
| `.asep/programs/px-exec.yaml` | Phase 2 scope, `implementation_gate: MB2-Q4-pass` |
| `.asep/capabilities/px-exec.yaml` | `px-exec-7…9` acceptance |
| `.asep/programs/px2-parallel.yaml` | Golden path reference program (§13.3) |
| `.asep/reports/MB2-PROMOTION-REVIEW-20260706.md` | Phase 2 entry authorized; promotion deferred |
| `.asep/reports/MB2-Q4-PLUGIN-REGISTRY-20260706.md` | Registry gate PASS — Phase 2 entry |

**Deferred to Phase 3+:** Dashboard UI, metrics/notification plugins, AgentProvider,
multi-program queue.

---

## Phase 2 DAG

```text
PX-EXEC-EWO-007  Merge Plugin (§8.2 merge)
      │
      ▼
PX-EXEC-EWO-008  Integration Plugin (§8.2 integration)
      │
      ▼
PX-EXEC-EWO-009  Qualification Plugin (§8.2 qualification)
```

| EWO | Title | Capability | SoR anchor | Depends on |
|-----|-------|------------|------------|------------|
| **PX-EXEC-EWO-007** | Merge Plugin | `px-exec-7-merge-plugin` | §8.2 merge, INV-R-03 | Wave A complete (001…006) |
| **PX-EXEC-EWO-008** | Integration Plugin | `px-exec-8-integration-plugin` | §8.2 integration, §7.3 | EWO-007 |
| **PX-EXEC-EWO-009** | Qualification Plugin | `px-exec-9-qualification-plugin` | §8.2 qualification, §7.3 | EWO-008 |

**First executable EWO:** `PX-EXEC-EWO-007` (MB2-Q4-pass satisfied; Plugin Registry operational).

**Sequencing:** Strictly serial — each plugin wires Rule Engine → Registry → events for
the next lifecycle stage. No parallel dispatch across 007…009.

---

## Golden path binding (§13.3)

Reference program: `.asep/programs/px2-parallel.yaml`

Rule pack fixture: `builder_engine/fixtures/px2_parallel_rules.yaml` (from EWO-002)

| Rule id | Trigger | Plugin |
|---------|---------|--------|
| `post-ewo-merge` | `EwoCompleted` + deps satisfied | `merge` |
| `post-merge-integration` | `MergeCompleted` + `ci_status: passed` | `integration` |
| `post-integration-qwo` | `IntegrationPassed` + `coverage_gate: passed` | `qualification` |

Phase 2 exit enables **live plugin execution** for golden path replay evidence. Full §13.3
PASS requires EWO-009 complete plus audited or automated replay bundle (separate act).

---

## Execution model

```text
MB2-Q1…Q6 PASS + promotion review
  → AUTHORIZE Phase 2 plugin dispatch  ← DONE @ 2026-07-06
  → backlog + proposals registered
  → AUTHORIZE PX-EXEC-EWO-007 → implement → verify → report
  → AUTHORIZE PX-EXEC-EWO-008 → …
  → AUTHORIZE PX-EXEC-EWO-009 → …
  → Phase 2 integration + §13.3 replay (separate authorization)
```

---

## Scope guard

| In scope | Out of scope |
|----------|--------------|
| `builder_engine/merge.py` — MergePlugin | Product Plane (`backend/app/**`, `frontend/**`) |
| `builder_engine/integration.py` — new | SoR normative edits |
| `builder_engine/qualification.py` — new | PX-4 |
| Plugin Registry wiring for P2 interfaces | Phase 3 dashboard/metrics |
| Event emission (`MergeCompleted`, etc.) | MB2 promotion / `mb2-complete` tag |
| Unit + integration tests per EWO | Git merge in Runtime process |

---

## WO-TRACE

```text
Wave A PASS → MB2-Q1…Q6 PASS → promotion review (§13.3 PARTIAL)
  → AUTHORIZE Phase 2 dispatch → EWO-007…009 proposals registered
  → WAIT: AUTHORIZE PX-EXEC-EWO-007
```
