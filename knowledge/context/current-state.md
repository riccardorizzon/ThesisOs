# Current State

> Snapshot as of **2026-06-25**. Branch: `main`.

## Where are we?

**Era II constitution frozen. MB2 + M5 specs frozen. Terminology migration started.**

```text
Era I   Execution Foundation     ✅  M0–M4 + MB1 Ph 1–2
Era II  Adaptive Workflow Intel  🟡  MB2 spec frozen — impl on mb2-adaptive-runtime next
Product Track                      M5 spec frozen — impl after Critic sign-off recorded
Platform Track                     MB2 plan ready; no code before branch work
```

## ASEP vocabulary

Official terms per ADR-0026. Migration tracker: `docs/platform/terminology-migration.md`.

## Frozen specs (parallel 2026-06-25)

| Track | Spec | Plan | ADR |
|-------|------|------|-----|
| Platform MB2 | `docs/superpowers/specs/2026-06-25-thesisos-mb2-adaptive-runtime-design.md` | `plans/mb2-adaptive-runtime-plan.md` | — |
| Product M5 | `docs/superpowers/specs/2026-06-25-thesisos-m5-tool-router-orchestration-design.md` | `plans/m5-tool-router-plan.md` | ADR-0027 |

## What is next?

1. **MB2 implementation** — branch `mb2-adaptive-runtime`, translate runtime-model phases
2. **M5 implementation** — branch `m5-tool-router` after explicit Critic pass on spec §12
3. **Terminology** — incremental per `terminology-migration.md` checklist

See `context/next-actions.md`.
