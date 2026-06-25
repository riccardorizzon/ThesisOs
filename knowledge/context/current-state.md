# Current State

> Snapshot as of **2026-06-25**. Branch: `main`.

## Where are we?

**Era II opened as formalization-first (ADR-0028). Platform constitution layered; MB2 impl re-scoped.**

```text
Era I   Execution Foundation     ✅  M0–M4 + MB1 Ph 1–2
Era II  Adaptive Workflow Intel  🟡  L0–L1 frozen; L2 (Global State Machine) next; then MB2 impl
Product Track                      M5 spec frozen — impl after Critic sign-off (orthogonal, unblocked)
```

## Platform constitution (layered — ADR-0028)

| Layer | Artifact | Status |
|-------|----------|--------|
| L0 Meta Model (objects) | `docs/platform/engineering-meta-model.md` | ✅ frozen |
| L1 Invariants (laws) | `docs/platform/invariant-model.md` | ✅ frozen |
| L2 Global State Machine | extends `ADR-0025` | 🔴 next |
| L3 Runtime Cycle (dynamics) | `docs/platform/runtime-model.md` | ✅ frozen |
| L4+ Event bus / Policy engine / Planner | MB2+ impl | 🔴 after L2 + rebase |

Principle: **define the model first; every component concretizes it.** Invariants are fail-closed laws, distinct from tunable policies. Meta model is platform-only; `Milestone` is the sole boundary object.

## ASEP vocabulary

Official terms per ADR-0026 (§8 refined by ADR-0028). Migration tracker: `docs/platform/terminology-migration.md`. Pending code rename: `WorkflowRuntime → EngineeringRuntime`.

## Frozen specs

| Track | Spec | Plan | ADR |
|-------|------|------|-----|
| Platform MB2 (impl) | `…-mb2-adaptive-runtime-design.md` ⚠️ re-scoped to L4+, freeze re-opened | `plans/mb2-adaptive-runtime-plan.md` (on hold) | ADR-0028 |
| Product M5 | `…-m5-tool-router-orchestration-design.md` | `plans/m5-tool-router-plan.md` | ADR-0027 |

## What is next?

1. **L2 — Global State Machine** — formalize project+packet states extending ADR-0025
2. **Rebase MB2 impl spec** on L0–L2, re-freeze, then implement (event bus, policy engine, replan)
3. **M5 implementation** — after explicit Critic pass on spec §12 (orthogonal)
4. **Terminology** — incremental; `WorkflowRuntime` rename on MB2 branch

See `context/next-actions.md`.
