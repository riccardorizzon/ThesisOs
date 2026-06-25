# ASEP — Era Model

- **Status:** Frozen (Architect 2026-06-25)
- **Scope:** Conceptual architecture of the **Adaptive Software Engineering Platform (ASEP)** — how Product Track and Platform Track coexist across Eras. **Not** an implementation roadmap or sprint plan.
- **Authority:** ADR-0026 (terminology). Supersedes informal "Agent OS" era language in historical docs.
- **Companion:** `docs/platform/runtime-model.md` (the engineering cycle processor)

---

## 1. What ASEP is

ASEP is the union of:

1. **Product Plane** — ThesisOS as shipped software (chat, memory, documents, retrieval, …).
2. **Build Control Plane** — how the codebase is planned, governed, observed, and promoted.
3. **Engineering Runtime** — deterministic execution of the engineering cycle (build/test/merge/promote loop).
4. **Execution workers** — LLM agents, humans, and future workers that perform non-deterministic work units.
5. **Contracts & governance** — OpenAPI, schema, ADRs, frozen specs, promotion gates.

```text
┌─────────────────────────────────────────────────────────────────────────┐
│              Adaptive Software Engineering Platform (ASEP)               │
│                                                                          │
│  ┌──────────────────────┐      ┌──────────────────────────────────────┐ │
│  │    Product Plane      │      │         Build Control Plane           │ │
│  │  (M-track)            │      │  plans · ADR · knowledge · policies   │ │
│  │  backend · frontend   │      │  orchestrate-builders (operator UI)   │ │
│  └──────────┬───────────┘      └───────────────────┬──────────────────┘ │
│             │ served to users                       │ governs             │
│             │                                       ▼                     │
│             │                      ┌────────────────────────────────────┐ │
│             │                      │       Engineering Runtime           │ │
│             │                      │  observe → … → replan (see runtime) │ │
│             │                      └───────────────────┬──────────────────┘ │
│             │                                          │ dispatches          │
│             │                                          ▼                     │
│             │                      ┌────────────────────────────────────┐ │
│             │                      │     Execution workers (LLM/human)   │ │
│             │                      └────────────────────────────────────┘ │
│  └──────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

The Product Plane and Platform Track evolve **in parallel**. Product milestones deliver user value; Platform milestones deliver factory intelligence. Neither replaces the other.

---

## 2. Tracks within ASEP

### Product Track (M-series)

| Property | Value |
|----------|-------|
| Goal | Ship ThesisOS capabilities to end users |
| Milestones | M0 Foundations … M18 (roadmap) |
| Spec location | `docs/superpowers/specs/`, milestone plans in `plans/` |
| Promotion | `docs/m{n}-promotion.md`, git tag `m{n}-complete` |
| Runtime touched | Product Plane only (`backend/app`, `frontend`) |

**Era I product outcome:** M0–M4 complete (`m0-complete` … `m4-complete`).

### Platform Track (MB-series)

| Property | Value |
|----------|-------|
| Goal | Make engineering work repeatable, observable, and eventually adaptive |
| Milestones | MB1 Build Workflow Engine … MBn (defined per Era) |
| Spec location | `docs/superpowers/specs/` (MB specs), `docs/platform/` (cross-cutting) |
| Promotion | Phase gates (`docs/mb{n}-phase*-gate.md`), optional tags |
| Runtime touched | Sidecars (`builder_engine/`, future engines) — **never** product imports |

**Era I platform outcome:** MB1 Phases 1–2 (graph read-model + packet workflow runtime).

---

## 3. Eras — platform maturity

Eras describe **how intelligent the factory is**, not which product feature ships next.

### Era I — Execution Foundation ✅

**Theme:** Replace ad-hoc agent orchestration with deterministic execution and frozen contracts.

| Delivered | Evidence |
|-----------|----------|
| Product foundation M0–M3 | Tags `m0-complete` … `m3-complete` |
| Conversation + memory seams | M1, M2 |
| Document ingestion | M3 |
| Retrieval loop closed | M4 — `RetrievalService`, `/search`, retriever node |
| Engineering Runtime v1 | MB1 Ph 1–2 — `builder_engine`, ADR-0025 packet FSM |
| Global discipline proven | Vision → Spec Freeze → Engine → Implementation → Validation |

**Architectural ceiling of Era I:** The Engineering Runtime executes **packets** reliably. The Control Plane is still mostly files + human/LLM operator. No global project FSM, no build event bus, no adaptive replanning, no observability dashboard.

**Declared closed:** 2026-06-25 (post `m4-complete`, MB1 Phase 2 gate).

---

### Era II — Adaptive Workflow Intelligence 🟡

**Theme:** The Control Plane and Runtime share a **frozen processor model**. Workflows become event-driven and observable; replanning is systematic, not heroic.

**Constitution (frozen before MB2 code):**

| Artifact | Role |
|----------|------|
| ADR-0026 | Terminology |
| This document | Era boundaries + track interaction |
| `runtime-model.md` | Engineering cycle processor |

**Target capabilities (implementation follows frozen specs):**

| Capability | Intent |
|------------|--------|
| Unified project/workflow state | Single derived view of era, epic, wave, blockers |
| Build event bus | Typed events; reactive handlers |
| Observability layer | Queue, bottlenecks, error rate, active tasks |
| Adaptive planner | Failure → dependency recalc → new tasks |
| Policy engine | Declarative rules replace scattered `if` |
| Runtime abstraction | `ExecutionRuntime` interface; builder = one adapter |

**MB2 meaning (post-freeze):** Implement the **Engineering Runtime** and Control Plane hooks defined in `runtime-model.md` — not "add a FSM" as an isolated feature.

**Product Track in Era II:** M5+ specs continue under Product Track rules; they **consume** Platform improvements (e.g. better validation stages) but do not define Platform architecture.

---

### Era III — Autonomous Engineering ⬜

**Theme:** Minimal human intervention in routine epics — planner proposes, policy approves, runtime executes, validation promotes.

Indicators (directional, not commitments):

- Epic-level autonomy with human approval gates only at Promotion and ADR freeze.
- Cross-epic dependency management.
- Automated rollback / recovery policies.
- Reviewer and Researcher workers as first-class execution types.

---

### Era IV — Self-Optimizing Platform ⬜

**Theme:** The platform improves its own throughput and quality — policy tuning, stage quarantine, cost/latency tradeoffs, predictive bottlenecks.

Indicators (directional):

- Metrics-driven replanning.
- Flaky-check quarantine (MB1 spec failure mode).
- Optional multi-runtime scheduling (builders + CI + deploy).

---

## 4. How tracks interact in an Era

```text
                    Human strategic intent
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
     Product spec freeze (M5…)        Platform spec freeze (MB2…)
              │                               │
              ▼                               ▼
     Product implementation          Runtime / Control Plane impl
              │                               │
              └───────────────┬───────────────┘
                              ▼
                    Shared validation (make ci, gates)
                              ▼
              Product promotion (m{n}-complete)
              Platform promotion (mb{n} gate)
```

**Sequencing rule (unchanged):** If Platform schedule/sync must understand Product job semantics (embedding stages, indexed status, …), **Product spec freezes first** (ADR-0025).

---

## 5. What Era II is not

| Misread | Reality |
|---------|---------|
| "Replace M-series with Eras" | Eras = platform maturity; M-series = product scope |
| "MB2 = global FSM ticket" | MB2 = implement frozen runtime + control hooks |
| "Skip specs for platform work" | ADR-0026 §5 applies to every MB phase |
| "Merge product and builder_engine" | Sidecar isolation remains (ADR-0023) |

---

## 6. Freeze record

- [x] Era I closure criteria documented
- [x] Era II–IV directional scope (non-binding detail until per-MB specs)
- [x] Product Track vs Platform Track interaction defined
- [x] Terminology aligned with ADR-0026

**Next authorized work:** Platform specs derived from `runtime-model.md` (MB2 design spec + ADR if needed) — **not** MB2 implementation until those freeze.

---

## 7. References

- ADR-0026 Platform Model & Terminology
- `docs/platform/runtime-model.md`
- ADR-0023, ADR-0025, ADR-0010
- `docs/m4-promotion.md`, `docs/mb1-phase2-gate.md` (Era I evidence)
