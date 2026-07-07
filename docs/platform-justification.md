# Platform Justification

> **Document class:** Architectural contract — hypotheses, validated value, exit criteria  
> **Status:** Active — ASEP Core 1.0 maintenance (ADR-0043, 2026-07-07)  
> **Audience:** Architect, operators, EWO authors  
> **Release:** `docs/asep-1.0-release.md`  
> **Does not replace:** Constitution, ADRs, SoR, Engineering Program — it binds *investment* decisions

This document states **what the platform layer has proven**, **what it assumes**,
**when to stop funding it**, and **what it does not own**. It is not a defense of
ASEP; it is the falsifiable contract between vision and implementation.

**Companion docs (how, not why):**

| Doc | Role |
|-----|------|
| `docs/engineering-program.md` | WorkOrder types, program stack |
| `docs/asep-capability-model.md` | Capability / QWO taxonomy |
| `.asep/programs/px-exec.yaml` | PX-EXEC delivery program (R&D track) |
| `knowledge/context/next-actions.md` | Product-first operating mode (provisional) |

---

## Program modes (resolves maintenance vs PX-EXEC)

Two tracks coexist by design. Ambiguity is a process failure, not an architecture
failure, unless this section is ignored.

| Track | Mode | Scope | Pull policy |
|-------|------|-------|-------------|
| **ASEP Core** | **Maintenance (1.0)** | CI gates, isolation, drift, QWO/STOP, platform contract, classification registry | ADR-0043 — change only on break/fix or **reproducible product block** |
| **PX-EXEC** | **R&D — frozen (post 1.0)** | Reference implementation per program graph; **no new phases/EWOs** until promotion criteria in `docs/asep-1.0-release.md` | Program yaml may record past delivery; **pull policy** is ADR-0043 |
| **Product programs** | Delivery | `backend/app/`, `frontend/` under Engineering Program graphs (PX-1…PX-3, thesis-agent, …) | User-perceivable capability is the primary progress metric |

**Rule:** New platform capabilities **do not enter ASEP Core** until promoted from
Category C → B → A (§5). PX-EXEC work remains Category C until MB2-Q gates pass
(§3 exit criteria).

**Explicit statement:** PX-EXEC is an **R&D program** to qualify an Engineering
Runtime — not proof that every Core maintenance constraint was waived. Product
dogfood and milestone delivery remain authoritative per `next-actions.md`.

---

## 1. Current validated value

Only capabilities with **repository evidence** are listed. “Improves quality” without
a cited artifact is excluded.

### V-01 — Sidecar runtime isolation

| Field | Value |
|-------|-------|
| **Claim** | Build-time sidecars must not import `backend.app` |
| **Evidence** | `make isolation`; `.github/workflows/ci.yml` job `isolation`; `.pre-commit-config.yaml` hook `runtime-isolation` |
| **ADR** | ADR-0019, ADR-0023 |
| **Category** | **A — Validated** |

### V-02 — Schema drift detection

| Field | Value |
|-------|-------|
| **Claim** | ORM models and `contracts/db/schema.sql` stay aligned |
| **Evidence** | `backend/tests/test_schema_snapshot.py`; CI backend pytest stage |
| **Category** | **A — Validated** |

### V-03 — Unified local/CI validation pipeline

| Field | Value |
|-------|-------|
| **Claim** | Same gates locally (`make ci`) and in GitHub Actions |
| **Evidence** | `Makefile` targets `lint`, `typecheck`, `unit`, `unit-frontend`, `unit-builder-engine`, `drift`, `isolation`; `.github/workflows/ci.yml` |
| **Gap** | `make scope` is **not** in GitHub CI (local only) |
| **Category** | **A — Validated** (with noted gap) |

### V-04 — Qualification workflow (STOP / QWO)

| Field | Value |
|-------|-------|
| **Claim** | Failed QWO halts progression; investigation can drive minimal product fix |
| **Evidence** | `.asep/reports/stop-20260630-c3-r2-fail.md`; `.asep/reports/C.3-R2-investigation.md`; `.asep/reports/EWO-4-runtime-grounding-alignment.md`; product changes in `backend/app/graph/prompt_wire.py`, `backend/app/graph/inference_enforcement.py` |
| **Policy** | `docs/auto-approval-policy.md`, `docs/termination-policy.md` |
| **Category** | **A — Validated** (thesis-agent migration track) |

### V-05 — Authorization gate (no executable WorkOrder → STOP)

| Field | Value |
|-------|-------|
| **Claim** | Platform dispatch without a registered EWO stops instead of improvising |
| **Evidence** | `.asep/reports/stop-20260705-px-exec-no-ewo.md`; `.asep/resolvers/authorize.md` |
| **Category** | **A — Validated** (governance behavior; manual/agent-enforced) |

### V-06 — MB2 Era I Engineering Runtime (build-time)

| Field | Value |
|-------|-------|
| **Claim** | Deterministic observe → policy → plan → cycle → schedule → sync path with tests |
| **Evidence** | `docs/mb2-phase-gate.md`; `builder_engine/` (D1–D10); `make unit-builder-engine` (75 tests); `plans/builder/STATE.yaml` status `closed` |
| **Limit** | `.builder-engine/events.jsonl` — 10 lines, last activity 2026-06-28; **operational cadence not evidenced** |
| **Category** | **A — Validated (build-time)**; not validated as daily operator loop |

### V-07 — Product Runtime Event Bus (M5)

| Field | Value |
|-------|-------|
| **Claim** | Product plane emits/consumes typed runtime events |
| **Evidence** | `backend/app/runtime/event_bus.py`; `backend/tests/test_runtime_event_bus.py`, `test_runtime_event_contract.py`; ADR-0030, `docs/runtime-constitution.md` |
| **Scope note** | **Product plane**, not Engineering Runtime — see §4 |
| **Category** | **A — Validated** |

### V-08 — Layer declaration on product PRs

| Field | Value |
|-------|-------|
| **Claim** | PRs touching `backend/app/` declare Business / Runtime / Infrastructure layer |
| **Evidence** | `.github/pull_request_template.md`; ADR-0030; `docs/architecture-decision-checklist.md` |
| **Limit** | Checklist is **manual** — not enforced by CI |
| **Category** | **A — Validated** (process); automation partial |

---

## 2. Platform hypotheses

Each entry is an **investment**, not a fact. Status must be updated when evidence
changes. IDs are stable for EWO traceability.

### H-01 — Rule Engine reduces repeated policy violations

| Field | Value |
|-------|-------|
| **Statement** | Declarative rules in YAML replace ad-hoc agent policy checks for engineering cycles |
| **Component** | PX-EXEC-EWO-002; SoR §7; ADR-0042 |
| **Status** | **Not demonstrated** — no rule engine in `builder_engine/` |
| **Success metric** | ≥3 policy rules evaluated in `builder-engine cycle`; zero manual policy overrides in audit log for 5 consecutive cycles |
| **Promotion to A** | MB2-Q-004 pass + green `make unit-builder-engine` with rule suite |

### H-02 — Dependency Engine prevents incorrect parallel merge order

| Field | Value |
|-------|-------|
| **Statement** | Execution graph derivation enforces packet `depends_on` before merge |
| **Component** | PX-EXEC-EWO-003; SoR §4.2, §5 |
| **Status** | **Not demonstrated** |
| **Success metric** | Document ≥1 incident where manual orchestration caused wrong merge order **or** dry-run replay of PX-2 wave shows ordering enforced without human merge script |
| **Promotion to A** | MB2-Q-001…Q-003 pass |

### H-03 — Engineering Event Bus replaces manual orchestration telemetry

| Field | Value |
|-------|-------|
| **Statement** | Append-only bus is the authoritative audit trail for engineering cycles |
| **Component** | PX-EXEC-EWO-001 (partial); `builder_engine/events.py`; `.builder-engine/events.jsonl` |
| **Status** | **Partially implemented, not operational** — catalog extended 2026-07-06; log stale since 2026-06-28 |
| **Success metric** | ≥20 engineering cycles logged in 90 days with `program_id` attribution |
| **Promotion to A** | MB2-Q-002 pass + operational log evidence |

### H-04 — Plugin registry reduces runtime coupling

| Field | Value |
|-------|-------|
| **Statement** | Merge / Integration / Qualification run as registered plugins, not skill steps |
| **Component** | PX-EXEC Phase 2; ADR-0042 § plugin registry |
| **Status** | **Not demonstrated** — Phase 2 not authorized |
| **Success metric** | ≥3 plugins; zero direct imports between plugin modules and `scheduler` internals |
| **Promotion to A** | MB2-Q-004 pass; PX-2 parallel replay via Runtime (dry-run then live) per `px-exec.yaml` |

### H-05 — Program Graph is reusable across products

| Field | Value |
|-------|-------|
| **Statement** | `.asep/programs/*.yaml` + Capability Graph govern any document-engineering program, not only ThesisOS |
| **Component** | `docs/engineering-program.md`; `docs/asep-capability-model.md`; programs: `thesis-agent-migration`, `thesisos-product-v2`, `px-exec`, … |
| **Status** | **Partially demonstrated** — multiple programs executed; **second product domain** (e.g. ContractOS, ResearchOS per PX1-EWO-006 proposal) **not onboarded** |
| **Success metric** | Second Engineering Program with distinct product codebase using same QWO/wave pattern without forked governance docs |
| **Promotion to A** | Second program completes ≥1 wave with QWO PASS |

### H-06 — MB2 SoR conformance via product observation

| Field | Value |
|-------|-------|
| **Statement** | Product can observe Runtime contracts (projection, program graph, job FSM) without implementing Runtime |
| **Component** | PX-3; `backend/app/services/conformance/`; `backend/app/api/conformance.py` |
| **Status** | **Observable, not qualified** — PX-3 Conformance Log: **0 entries**; assessment PASS (`.asep/reports/MB2-CONFORMANCE-ASSESSMENT.md`) |
| **Success metric** | SoR section promoted from Observable → Qualified per §13 gates |
| **Limit** | Conformance PASS ≠ Runtime implementation complete (assessment states this explicitly) |
| **Promotion to A** | Not applicable at platform level — spawns H-01…H-04 qualification |

### H-07 — Multi-product hosting on shared API surface

| Field | Value |
|-------|-------|
| **Statement** | ProjectContext enables ThesisOS, ContractOS, ResearchOS on one stack |
| **Component** | PX1-EWO-006; `backend/app/schemas/context.py` |
| **Status** | **Not demonstrated** — only ThesisOS consumer in production paths |
| **Success metric** | Second product ID with isolated program graph and dogfood session |
| **Promotion to A** | Second product milestone tagged |

---

## 3. Exit criteria (kill switches)

If an exit condition fires, the component **freezes**, **archives**, or **reverts to
simpler composition** — no “immortal framework” exception.

| ID | Component / hypothesis | Exit condition | Action |
|----|------------------------|----------------|--------|
| **X-01** | PX-EXEC Phase 1 (EWO-002+) | No Architect authorization receipt within **60 days** of backlog registration | Freeze px-exec implementation; spec-only |
| **X-02** | Engineering Event Bus (H-03) | `<5` new events in `.builder-engine/events.jsonl` over **90 days** while PX-EXEC active | Remove `builder_engine` from required CI; optional dev tool only |
| **X-03** | Plugin registry (H-04) | PX-EXEC Phase 2 completes with **<3 plugins** | Replace registry with direct composition; ADR amendment required |
| **X-04** | Program Graph reuse (H-05) | No second Engineering Program onboarded by **2026-12-31** | Freeze new program YAML templates; ThesisOS-only governance |
| **X-05** | Multi-product hosting (H-07) | No second product dogfood by **2026-12-31** | Remove ContractOS/ResearchOS from scope statements; close ProjectContext extension |
| **X-06** | MB2 Reference Implementation | MB2-Q1 not authorized within **180 days** of PX-EXEC authorization (2026-07-05) | Archive px-exec to maintenance; retain Era I sidecar only |
| **X-07** | `.asep/reports/` growth | Report count increases **>50** in a quarter **without** corresponding CI or product test additions | Mandatory archive pass; report required only for QWO FAIL, promotion, ADR |
| **X-08** | Conformance APIs in product | Explain/knowledge UX depends on YAML supervisor WAIT after PX-3 close | Remove gating; keep debug endpoints under `/dev/` only |

**Review cadence:** Operator reviews exit table at each milestone tag (`m*-complete`)
and at PX-EXEC EWO completion.

---

## 4. Scope boundaries

### ASEP Platform owns

| Area | Location | Notes |
|------|----------|-------|
| Engineering governance | `.asep/`, `.cursor/skills/asep/` | Programs, QWO, authorization, STOP |
| Qualification discipline | `.asep/pipeline/qualification.md`, QWO templates | Attestation + gates |
| Build-time Engineering Runtime | `builder_engine/`, `plans/builder/STATE.yaml` | Must not import product runtime |
| Builder agent memory (sidecar) | `builder_memory/` | Retrieval for agents; not product RAG |
| CI gates (platform-enforced) | `Makefile`, `.github/workflows/ci.yml`, `.pre-commit-config.yaml` | Isolation, drift, unit suites |
| Runtime Constitution (product) | `docs/runtime-constitution.md` | Governs **product** Runtime layer |

### ASEP Platform does **not** own

| Area | Location | Notes |
|------|----------|-------|
| Thesis business logic | `backend/app/graph/`, domain services | LangGraph agents, RAG, writing |
| Product UI | `frontend/` | Except optional conformance **debug** surfaces |
| Product retrieval / corpus | M4 services, indexers | Separate from builder_memory |
| Product orchestration | Conversation graph, tool router | M5+ product plane |
| Deploy pipeline | `infra/ci/cloudbuild.yaml` | Deploy-only today — **product infra debt** |
| User-facing thesis content | `knowledge/thesis-agent/` content | Domain Ground Truth, not platform |

### Hard rules

1. **No platform code in product hot paths** unless Category A and listed in §1.
2. **No product imports from `builder_engine/`** (enforced by V-01).
3. **New ideas default to product** until proven cross-program (H-05) or cross-cycle (H-01…H-04).

---

## 5. Evolution policy

Every new capability or EWO must declare **one category** in its proposal header.

### Category A — Validated

Stable platform or product contract. May appear in CI, operator runbooks, and
Architect promotion paths. Must cite §1 entry or newly collected evidence before
classification.

### Category B — Experimental

Implemented in repo but **not** yet qualified. May ship behind flags or dev routes.
Must link to a hypothesis (§2) and success metric. **Must not** block product delivery.

### Category C — Research

Spec, ADR, or authorized R&D program only (PX-EXEC default). No product dependency,
no user-facing behavior, no CI expansion unless explicitly authorized.

### EWO proposal header (required)

Template: `.asep/templates/platform-contract-block.md`

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  category: A | B | C
  hypothesis_id: H-0N | n/a
  success_metric: "<measurable>"
  exit_id: X-0N | n/a
  program_mode: core | product | rd
```

Retrospective backfill adds `classification_mode`, `classification_pass`, `classified_on`,
and `classification_registry` per `.asep/templates/platform-contract-block.md`.

**Registry (authoritative):** `.asep/registry/platform-classification.yaml`  
**CI validation:** `make validate-platform-classification`  
**Human index:** `.asep/reports/platform-classification-index.md`  
**Not consumed by product runtime.**

**Promotion path:** C → B (implementation + evidence) → A (metric satisfied + gate pass
or Architect ratification). **Demotion:** exit criteria (§3) fires → freeze or archive.

### Classification of current PX-EXEC backlog

| EWO | Title | Category |
|-----|-------|----------|
| PX-EXEC-EWO-001 | Event Model & Bus | **B** (implemented; H-03 metric not met) |
| PX-EXEC-EWO-002 | Rule Engine | **C** |
| PX-EXEC-EWO-003 | Dependency Engine | **C** |
| PX-EXEC-EWO-004…006 | Queue, Scheduler, Projection | **C** |

---

## 6. Decision protocol

When evaluating a platform proposal, ask in order:

1. **Which §1 validated capability does it extend?** If none → default **C**.
2. **Which §2 hypothesis does it test?** If none → reject or reframe as product work.
3. **What is the success metric?** If unmeasurable → reject.
4. **Which §3 exit criterion applies?** If none → add one before authorization.
5. **Does it violate §4 scope?** If yes → product milestone, not platform.
6. **Does it conflict with `next-actions.md` operating mode?** If yes → require explicit Architect exception citing this document § Program modes.

---

## 7. Evidence index (quick reference)

| Artifact | Path |
|----------|------|
| Operating mode (provisional) | `knowledge/context/next-actions.md` |
| PX-EXEC program | `.asep/programs/px-exec.yaml` |
| MB2 SoR | `docs/superpowers/specs/mb2-engineering-runtime-spec.md` |
| Engineering Runtime ADR | `decisions/ADR-0042-engineering-runtime.md` |
| MB2 phase gate (Era I) | `docs/mb2-phase-gate.md` |
| C.3-R2 STOP | `.asep/reports/stop-20260630-c3-r2-fail.md` |
| PX-EXEC empty backlog STOP | `.asep/reports/stop-20260705-px-exec-no-ewo.md` |
| PX-3 conformance assessment | `.asep/reports/MB2-CONFORMANCE-ASSESSMENT.md` |
| CI workflow | `.github/workflows/ci.yml` |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-06 | Initial contract — post architecture review |
| 2026-07-07 | ASEP Core 1.0 maintenance freeze — ADR-0043, `docs/asep-1.0-release.md` |
