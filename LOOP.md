# Loop Configuration — ASEP (Adaptive Software Engineering Platform)

This repo implements **loop engineering** at platform scale. The community
pattern (STATE + trigger + maker/checker + verify + stop) maps to ASEP as
follows — see [cobusgreyling/loop-engineering](https://github.com/cobusgreyling/loop-engineering).

## Active Loops

| Loop | Trigger | Status | Operator surface |
|------|---------|--------|------------------|
| **Builder epic** | `orchestrate builders wave/sync` | L2 — assisted | `.cursor/skills/orchestrate-builders/SKILL.md` |
| **Engineering Runtime** | full loop: `observe→policy→plan→cycle→schedule→sync→events` | L3 — MB2 D1–D10 | `docs/mb2-phase-gate.md` |
| **AgentOS dev cycle** | per packet / milestone | L2 | `knowledge/development/workflow.md` |
| **Goal (session)** | `/goal` | L1 — session-scoped | `.claude/skills/goal/SKILL.md` |

**Last run:** 2026-06-28 — loop-engineering audit + ASEP mapping (manual; `npx @cobusgreyling/loop-audit` pending Node on dev VM).

## ASEP ↔ Loop Engineering Map

| Loop engineering primitive | ASEP artifact |
|----------------------------|---------------|
| State spine | `plans/builder/STATE.yaml` (+ bridge `STATE.md`) |
| Trigger | `wave` / `builder-engine schedule`, `/goal`, handoff start |
| Worktree isolation | `.worktrees/packet-*/` (orchestrate-builders §2C) |
| Maker | Cursor Task implementer / explorer workers |
| Checker | sync barrier + `required_checks` + integrator (never self-grade) |
| Verify | `builder-engine sync`, `make ci`, promotion gates |
| Stop condition | packet `done_criteria`, epic `close`, gate green |
| Replan | Era II `Replan` phase (human + Architect today) |

## Engineering Runtime Cycle (10 phases)

Frozen in `docs/platform/runtime-model.md`:

```text
Observe → Evaluate Policies → Plan → Schedule → Execute → Validate → Merge
  → Publish Events → Update State → Replan → (loop)
```

Era I vertical slice: **Schedule → Validate → Update State** (`builder_engine/runtime.py`).
Era II completes Observe, Policies, Merge (engine), Events, Replan.

## Human Gates

- No auto-merge without integrator pass and green `required_checks`
- Frozen specs/ADRs/contracts: workers must not edit without Architect re-freeze
- Denylist: auth, secrets, `.env`, production infra without explicit epic scope
- ASEP maintenance mode: platform changes only when product milestone is blocked (see `knowledge/context/next-actions.md`)

## Worktrees

- One git worktree per implementer packet (`.worktrees/packet-<id>/`)
- Never parallel implementers in the main workspace
- Sync barrier mandatory between waves

## Connectors (MCP)

- GitHub via `gh` for PR/issue workflows (babysit skill when needed)
- Product runtime (Vertex, Cloud SQL) is **not** in the builder loop (ADR-0002)

## Budget

See `loop-budget.md`. Kill switch: pause epic in STATE, `/goal pause`, or stop dispatch.

## Readiness (community audit)

Run when Node is available:

```bash
npx @cobusgreyling/loop-audit . --suggest
```

**Score (2026-06-28):** 100/100 · **L3** — verifier, triage, safety, budget skill present.

## Links

- Platform model: `docs/platform/era-model.md`, ADR-0026
- Builder bus: `plans/builder/README.md`
- Loop checklist: https://github.com/cobusgreyling/loop-engineering/blob/main/docs/loop-design-checklist.md
