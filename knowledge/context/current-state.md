# Current State

> Snapshot as of **2026-06-25**. Branch: `main` @ `m3-complete`.

## Where are we?

**M3 promoted (`m3-complete`). M4 retrieval spec frozen (Architect 2026-06-25). MB1 Phase 1 shipped; Phase 2 blocked until M4 Planner plan + runtime implementation per ADR-0025.**

```text
M0–M2           ✅ promoted
M3 Documents    ✅ m3-complete (merge e0a1620)
M4 Retrieval    🟡 spec frozen — implementation NOT started
MB1 Engine      🟢 Phase 1 done · Phase 2 next (runtime model in ADR-0025)
```

> `make ci` green. ⚠️ M3 DB integration tests **waived** — Docker containerd I/O error
> (2026-06-25). Re-run when Docker is repaired.

## Pipeline discipline (2026-06-25)

```text
Vision → Spec Freeze → Engine → Implementation → Validation
```

Not implementation-before-spec. M4 spec frozen before MB1 Phase 2 schedule/sync.

## What is next?

1. **Critic + Planner for M4** — sign-off on frozen spec → `plans/m4-retrieval-system-plan.md`
2. **MB1 Phase 2** — execution state machine + runtime loop (ADR-0025); CLI as views
3. **M4 implementation** — only after plan + Phase 2 engine foundation
4. **Docker fix** — optional: run waived M3 DB integration tests for full evidence

See `context/next-actions.md`.
