---
name: orchestrate-builders
description: >-
  Orchestrate parallel Cursor builder agents with isolated git worktrees,
  shared STATE bus, work-packet DAG, and wave sync barriers. Use when building
  ThesisOS across backend/frontend/infra with multiple agents in parallel trees
  that must stay in sync.
user_invocable: true
triggers:
  - orchestrate builders
  - builder orchestration
  - parallel builder agents
  - run builder wave
  - sync builder wave
  - start builder epic
argument-hint: "[start|wave|sync|status|close] [epic-name]"
---

# Orchestrate Builders

Parallel builder-agent orchestration for ThesisOS development. **Worktrees for
implementers** (safe isolation), **file locks in STATE** for explorers/reviewers,
**wave barriers** for sync.

**Guards:**
- **Not plan mode.** Writes files and creates worktrees. Exit plan mode first.
- **Not runtime LangGraph.** This skill coordinates *Cursor agents building the
  codebase*, not ThesisOS runtime multi-agent (M12).
- **Never parallel implementers in one worktree.** One worktree per implementer
  packet in a wave.
- **Never skip the sync barrier** between waves.

**Arguments:** $ARGUMENTS

---

## Quick Reference

**ASEP operator surface (ADR-0026):** This skill is the human/LLM **operator surface** on the **Build Control Plane**. Deterministic orchestration decisions are delegated to the **Engineering Runtime** (`builder-engine` CLI). Execution workers (Cursor Task agents) implement packets in isolated worktrees.

| Command surface | Action |
|-----------------|--------|
| `start <epic>` | Init epic from plan/handoff → STATE + packet files |
| `wave` | Dispatch ready packets in current wave (parallel Task agents) |
| `sync` | Barrier: collect results, validate, merge worktrees, advance wave |
| `status` | Print STATE summary (packets, locks, blockers) |
| `close` | Final integrator pass + handoff prompt for next session |

**Deterministic engine (MB1 Phase 1 — prefer over prose):**

| Engine command | Replaces |
|----------------|----------|
| `builder-engine lint-graph` | `validate-state.sh`, §1 packet rules |
| `builder-engine observe` | Preflight snapshot (MB2 D1) |
| `builder-engine policy` | Evaluate policies (MB2 D2) |
| `builder-engine plan` | Extended plan + critical path (MB2 D3) |
| `builder-engine cycle --dry-run` | Full preflight Observe→Policy→Plan (MB2 D6) |
| `builder-engine status` | Manual STATE summary |
| `builder-engine ready` | §2A ready-set computation |
| `builder-engine schedule` | §2 wave dispatch — claim, locks, manifest |
| `builder-engine sync` | §3 barrier — VALIDATING, wave advance |
| `builder-engine check <stage>` | Named Makefile stage runner |

---

## Architecture

```text
Build Control Plane — operator surface (this session / orchestrate-builders skill)
  ├── Planner      → epic → work packets (DAG) in plans/builder/
  ├── Dispatcher   → fan-out execution workers (Cursor Task agents) per ready packet
  ├── Sync         → barrier: checks, merge worktrees, update STATE
  └── Integrator   → cross-package validation after last wave

Engineering Runtime (builder_engine/) — deterministic control decisions
  ├── lint-graph / ready / schedule / sync / check
  └── reads STATE + packets; never source of truth (ADR-0023, ADR-0026)
```

**Communication channels:**

1. **`plans/builder/STATE.yaml`** — sync bus (packet status, decisions, locks)
2. **`plans/builder/packets/*.yaml`** — packet specs (ownership, deps, checks)
3. **Handoff/Plan files** — narrative context (`plans/handoffs/`, `PLAN_*.md`)
4. **Git worktrees** — physical isolation at `.worktrees/packet-<id>/`

---

## Prerequisites

Before first wave:

1. **Epic scope** — a `PLAN_*.md`, handoff, or milestone spec (e.g. M1 design spec).
2. **Worktree directory** — `.worktrees/` (gitignored). Verify:

```bash
git check-ignore -q .worktrees 2>/dev/null || echo "WARN: add .worktrees/ to .gitignore"
```

3. **STATE initialized** — copy `plans/builder/STATE.example.yaml` → `plans/builder/STATE.yaml`
   and fill `epic`, `decisions`, `packets`.

**Related skills (invoke as needed):**

| Phase | Skill |
|-------|-------|
| Plan → packets | `handoffplan`, `writing-plans` |
| Worktree setup | `using-git-worktrees` |
| Fan-out dispatch | `dispatching-parallel-agents` |
| Per-packet review | `subagent-driven-development` (sequential, post-merge) |
| Session close | `handoff` |

---

## Step 1: Start Epic (`start <epic>`)

1. Read the epic plan/spec. Extract **decisions** (frozen contracts, ADRs, anti-goals).
2. Decompose into work packets. Rules:
   - **One owner per file per wave** — no overlapping `owned_files` within a wave.
   - **Explorer packets** (wave 1): read-only analysis, no worktree needed.
   - **Implementer packets** (wave 2+): code changes, **require worktree**.
   - **Integrator packet** (final wave): merge + cross-package tests.
3. Write packet files: `plans/builder/packets/<id>.yaml` (see template).
4. Write `plans/builder/STATE.yaml`:
   - `epic`, `chain`, `wave: 1`
   - `decisions` from plan anti-goals + frozen contracts
   - `packets` summary (status `ready`, wave, depends_on)
   - `file_locks: {}` (populated when wave starts)
5. Announce packet table to user before dispatching.

Use [`references/packet-template.yaml`](references/packet-template.yaml) and
[`references/agent-prompt-templates.md`](references/agent-prompt-templates.md).

---

## Step 2: Dispatch Wave (`wave`)

### 2A: Identify ready packets

Run the engine (preferred):

```bash
builder-engine ready --repo-root .
```

A packet is **ready** when:

- `status: ready`
- All `depends_on` packets have `status: done`
- Current `wave` in STATE matches packet `wave`

If none ready but wave incomplete → run `sync` first or fix blockers.

### 2B: Lock files

For each ready packet, set `file_locks` in STATE to owned paths before dispatch:

```yaml
file_locks:
  backend/app/llm/: P4
  frontend/lib/api.ts: P6
```

Mark packets `status: in_progress`. Commit STATE update (optional but recommended).

### 2C: Prepare worktrees (implementers only)

For each **implementer** packet in the wave:

```bash
PACKET_ID=P4
BRANCH="builder/${EPIC}-${PACKET_ID}"
WORKTREE=".worktrees/packet-${PACKET_ID}"

git worktree add -b "$BRANCH" "$WORKTREE" HEAD
```

Explorers and reviewers run in the main workspace (read-only or single-file edits).

Follow `using-git-worktrees` for safety checks.

### 2D: Fan-out Task agents (parallel)

Launch **one Task per ready packet in a single message** (parallel dispatch).

Each prompt must be **self-contained** — see agent prompt templates. Include:

- **Builder Memory context** (optional but recommended): run `builder-memory retrieve --task "…" --role <agent_type> --epic <epic> --packet <id>` and paste the `NON-AUTHORITATIVE` block (see `knowledge/development/builder-memory.md`). Preflight: `.cursor/skills/orchestrate-builders/scripts/builder-memory-preflight.sh`
- Packet ID, wave, depends_on (with outputs from completed deps)
- `owned_files` and explicit **DO NOT touch** list
- `decisions` from STATE (verbatim)
- Completed dependency `output` summaries from STATE
- Worktree path (implementers): `Full Repository Path: <worktree abs path>`
- Return contract: `DONE | BLOCKED | NEEDS_CONTEXT | DONE_WITH_CONCERNS`

**Agent types → subagent_type:**

| agent_type | subagent_type | model hint |
|------------|---------------|------------|
| explorer | explore | fast |
| implementer | generalPurpose | standard |
| reviewer | generalPurpose | capable |
| integrator | generalPurpose | capable |

**Do NOT** dispatch multiple implementers in the same worktree or without file locks.

---

## Step 3: Sync Barrier (`sync`)

**Mandatory between waves.** Do not start the next wave until sync passes.

### 3A: Collect agent returns

For each `in_progress` packet, record in STATE:

```yaml
packets:
  P4:
    status: done          # or blocked
    output: "3 bullets..."
    checks:
      - cmd: "pytest backend/tests/test_llm.py -q"
        result: "5 passed"
    integration_notes: "factory.py needs get_llm_client in main startup"
```

### 3B: Run validation script

```bash
.cursor/skills/orchestrate-builders/scripts/validate-state.sh
```

Fix any reported errors before continuing.

### 3C: Merge worktrees (implementers)

For each done implementer packet with a worktree:

```bash
PACKET_ID=P4
BRANCH="builder/${EPIC}-${PACKET_ID}"

# In main repo
git fetch . "refs/heads/${BRANCH}:refs/heads/${BRANCH}" 2>/dev/null || true
git merge --no-ff "$BRANCH" -m "merge(builder): packet ${PACKET_ID} for ${EPIC}"
```

If merge conflicts:

1. Assign **integrator** or orchestrator resolves in main workspace.
2. Record resolution in STATE `integration_notes`.
3. Re-run packet `required_checks` after merge.

### 3D: Cross-packet checks

Run wave-level checks from packet specs or plan (e.g. `pytest`, `npm test`, `terraform validate`).

### 3E: Advance wave

1. Clear `file_locks`.
2. Increment `wave` in STATE.
3. Mark next-wave packets `status: ready` if deps satisfied.
4. Remove worktrees for merged packets:

```bash
git worktree remove ".worktrees/packet-${PACKET_ID}" --force
git branch -d "builder/${EPIC}-${PACKET_ID}"  # after merge
```

### 3F: Sync decision

| Outcome | Action |
|---------|--------|
| All packets in epic `done` | Run final integrator or `close` |
| Next wave has ready packets | User may run `wave` again |
| Blocked packets | Document in STATE `blockers`, do not advance wave |

See [`references/wave-sync-checklist.md`](references/wave-sync-checklist.md).

---

## Step 4: Close Epic (`close`)

1. Run integrator packet if not done (full test suite, OpenAPI diff, lint).
2. Update STATE `status: closed`.
3. Run `/handoff` with epic summary.
4. Tell the user to run in a fresh session:

```
/handoff start
```

Include epic context in the handoff: Epic `${EPIC}` complete — read `plans/builder/STATE.yaml` and continue from [next milestone / follow-up tasks].

---

## Status (`status`)

Print:

- Epic, wave, chain
- Packet table: id · type · status · wave · deps
- Active `file_locks`
- Open `blockers`
- Worktrees: `git worktree list`

---

## Work Packet Rules (hard)

1. **One owner per file per wave** — enforced by `file_locks` + validate script.
2. **No parallel implementers without worktrees.**
3. **Explorers never modify production code** — analysis output only.
4. **Preserve `decisions`** — agents must not violate frozen contracts listed in STATE.
5. **Required checks must pass** before packet → `done`.
6. **Sync barrier** between waves — no exception.

---

## Example: M1 three-wave layout

| Wave | Packets (parallel) | agent_type | Isolation |
|------|-------------------|------------|-----------|
| 1 | P1 backend LLM · P2 graph/service · P3 frontend SSE | explorer | main repo |
| 2 | P4 LiteLLM · P5 ConversationService · P6 Chat UI | implementer | 3 worktrees |
| 3 | P7 integration tests + OpenAPI | integrator | main repo |

Wave 1 → `sync` → Wave 2 → `sync` → Wave 3 → `close`.

---

## Red Flags

**Never:**

- Dispatch parallel implementers in one workspace
- Skip sync between waves
- Merge worktrees before checks pass
- Let agents read STATE from memory — always cite current `STATE.yaml`
- Touch files outside `owned_files`
- Violate `decisions` in STATE (frozen GraphState, ADRs, etc.)

**If agent returns BLOCKED:**

1. Record blocker in STATE.
2. Orchestrator resolves or provides context.
3. Re-dispatch same packet (same worktree if implementer).

**If merge conflicts repeat:**

- Re-plan packet boundaries (smaller owned_files).
- Sequence previously parallel packets into separate waves.
