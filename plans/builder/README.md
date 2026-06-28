# Builder Agent Orchestration

Parallel Cursor agents building ThesisOS with **isolated git worktrees** for
implementers, a shared **STATE bus**, and **wave sync barriers**.

## Quick start

1. **Read the skill:** `.cursor/skills/orchestrate-builders/SKILL.md`
2. **Init state:** copy `STATE.example.yaml` → `STATE.yaml` and fill for your epic
3. **Add packets:** `packets/<id>.yaml` per work unit (see `PACKET.example.yaml`)
4. **Run waves:**
   - Orchestrator session: `wave` → agents work in parallel
   - `sync` → merge worktrees, validate, advance wave
   - Repeat until `close`

## Files

| File | Purpose |
|------|---------|
| `STATE.yaml` | Live bus — packet status, decisions, file locks, wave |
| `STATE.example.yaml` | Template for new epics |
| `packets/*.yaml` | Work packet specs (ownership, deps, checks) |
| `.worktrees/packet-*/` | Isolated workspaces (gitignored) |

## Roles

```text
Orchestrator (main session)
  wave 1: explorers (parallel, main repo, read-only)
  sync barrier
  wave 2: implementers (parallel, one worktree each)
  sync barrier + merge
  wave 3: integrator (main repo, full validation)
```

## Commands (orchestrator session)

Tell the agent:

- `orchestrate builders start m1-conversation` — init from plan/spec
- `orchestrate builders wave` — dispatch current wave
- `orchestrate builders sync` — barrier between waves
- `orchestrate builders status` — print STATE summary
- `orchestrate builders close` — finalize + handoff

## Validation

```bash
chmod +x .cursor/skills/orchestrate-builders/scripts/validate-state.sh
.cursor/skills/orchestrate-builders/scripts/validate-state.sh
```

## Rules (hard)

1. One file owner per wave — no overlapping `owned_files`
2. Implementers **always** in worktrees — never parallel edits in main workspace
3. Sync barrier between waves — no skipping
4. Respect `decisions` in STATE (frozen contracts, ADRs)

## Related skills

- `handoff` / `handoffplan` — session memory and phased plans
- `using-git-worktrees` — worktree safety
- `dispatching-parallel-agents` — fan-out pattern
- `subagent-driven-development` — post-merge review

## Example epic layout (M1)

| Wave | Packets | Type | Isolation |
|------|---------|------|-----------|
| 1 | P1 · P2 · P3 | explorer | main repo |
| 2 | P4 · P5 · P6 | implementer | 3 worktrees |
| 3 | P7 | integrator | main repo |

See skill § "Example: M1 three-wave layout" for details.

## Loop engineering (ASEP)

This bus is the **state spine** for ASEP's builder loop — the same role as
`STATE.md` in [loop-engineering](https://github.com/cobusgreyling/loop-engineering)
starters. Bridge docs at repo root: `LOOP.md`, `STATE.md` (pointer), `loop-budget.md`,
`loop-run-log.md`. Full platform cycle: `docs/platform/runtime-model.md`.

Policy rules (declarative): `plans/builder/policies.yaml` — evaluated by
`builder-engine policy` after observe.
