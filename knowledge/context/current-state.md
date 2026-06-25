# Current State

> Snapshot as of **2026-06-25**. Branch: `main`.

## Where are we?

**Era II constitution complete through L2. Platform GSM frozen. MB2 impl pending rebase.**

```text
Era I   Execution Foundation     ✅  M0–M4 + MB1 Ph 1–2
Era II  Adaptive Workflow Intel  🟡  L0–L3 frozen; L2 GSM frozen; L4 (MB2) next
Product Track                      M5 spec frozen — impl after Critic sign-off (orthogonal)
```

## Platform constitution (layered — ADR-0028)

| Layer | Artifact | Status |
|-------|----------|--------|
| L0 Meta Model (objects) | `docs/platform/engineering-meta-model.md` | ✅ frozen |
| L1 Invariants (laws) | `docs/platform/invariant-model.md` | ✅ frozen |
| L2 Global State Machine | `docs/platform/global-state-machine.md` | ✅ frozen |
| L3 Runtime Cycle (dynamics) | `docs/platform/runtime-model.md` | ✅ frozen |
| L4+ Event bus / Policy / Planner | MB2 impl | 🔴 rebase MB2 spec → implement per `plans/l2-global-state-machine-plan.md` |

Principle: **every engineering operation is a state transition**. The runtime executes transitions; nothing else.

## ASEP vocabulary

Official terms per ADR-0026 (§8 refined by ADR-0028). Pending code rename: `WorkflowRuntime → EngineeringRuntime`.

## Frozen specs

| Track | Spec | Plan | ADR |
|-------|------|------|-----|
| Platform L2 | `docs/platform/global-state-machine.md` | `plans/l2-global-state-machine-plan.md` | ADR-0028 |
| Platform MB2 (impl) | `…-mb2-adaptive-runtime-design.md` ⚠️ re-scoped L4+, rebase pending | on hold | ADR-0028 |
| Product M5 | `…-m5-tool-router-orchestration-design.md` | `plans/m5-tool-router-plan.md` | ADR-0027 |

## What is next?

1. **Rebase MB2 impl spec** on L2 GSM (trace every deliverable to transition ID)
2. **Implement L4** — Phases 1–7 in `plans/l2-global-state-machine-plan.md`
3. **M5 implementation** — after Critic §12 (orthogonal)

See `context/next-actions.md`.
