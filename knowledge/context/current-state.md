# Current State

> Snapshot as of **2026-06-25**. Branch: `main` @ `m4-complete`.

## Where are we?

**Era I closed. Era II constitution frozen — implementation not started.**

```text
Era I   Execution Foundation     ✅  M0–M4 + MB1 Ph 1–2
Era II  Adaptive Workflow Intel  🟡  ADR-0026 + platform docs frozen; MB2 spec next
Product Track                      M5+ awaits frozen spec
Platform Track                     MB2 blocked until MB2 spec freeze
```

> `make ci` green. DB integration tests waived (Docker I/O, 2026-06-25).

## ASEP vocabulary (official)

| Term | Meaning |
|------|---------|
| **ASEP** | Whole platform |
| **Product Plane** | M-track / ThesisOS runtime |
| **Build Control Plane** | Plans, ADR, knowledge, policies, operator skill |
| **Engineering Runtime** | Deterministic cycle executor (`builder_engine/` today) |

See ADR-0026, `docs/platform/era-model.md`, `docs/platform/runtime-model.md`.

## Global rule (all capabilities)

```text
Vision → Spec → ADR → Freeze → Implementation → Gate → Promotion
```

## What is next?

1. **MB2 spec** — translate `runtime-model.md` phases to modules (no code before freeze)
2. **M5 spec freeze** — Product Track (planner/router)
3. **Incremental doc migration** — replace legacy "Agent OS" when touching files

See `context/next-actions.md`.
