# Development Workflow — the AgentOS Loop

> Sources: `backend/app/db/models.py` (`agent_steps.phase` enum), `.cursor/skills/orchestrate-builders/SKILL.md`, M0/M1 plans (TDD red→green→commit), ADR-0001/0010, `plans/builder/STATE.yaml`, the `writing-plans` / `subagent-driven-development` / `verification-before-completion` skills.

ThesisOS is built (and ultimately runs) on a single development methodology — the
**AgentOS loop**. It is encoded directly in the data model: `agent_steps.phase ∈
{observe, hypothesis, plan, implement, test, critic, qa, revise, promote}`.

## The loop

```text
Observe → Hypothesis → Plan → Implement → Test → Critic → Revise → Promote
   ▲                                                          │
   └───────────────────────── (loop) ◄────────────────────────┘
```

| Phase | Goal | Builder practice | Artifact |
|-------|------|------------------|----------|
| **Observe** | Understand current reality | Read repo, contracts, current-state, STATE; no guessing | findings / explorer output |
| **Hypothesis** | State the intended change + expected outcome | "If we add X, then Y, measured by Z" | scope note |
| **Plan** | Turn a frozen spec into ordered TDD tasks / a packet DAG | `writing-plans`; `plans/builder/*` | plan + packets + STATE |
| **Implement** | Build the smallest correct increment | red → green → commit; stay in `owned_files` | code + tests |
| **Test** | Prove it works | pytest / tsc / build / smoke | green suite |
| **Critic** | Self/peer review for correctness & grounding | `code-reviewer`, Bugbot; runtime Critic for content | review notes |
| **Revise** | Fix what Critic found | targeted edits, new commits | fixes |
| **Promote** | Ship past an evidence-backed gate | merge → tag; ADR-0010 gate green | tag/release |

The loop repeats per task, per packet, and per milestone.

## How the phases map to the repo

- **Observe/Hypothesis** → the spec's "Context & Goal" + "Open Questions/Risks".
- **Plan** → `docs/superpowers/plans/*` and `plans/builder/{STATE,packets}`.
- **Implement/Test** → TDD tasks (every plan task is: write failing test → run (fail)
  → implement → run (pass) → commit).
- **Critic/Revise** → review subagents + the recorded review fixes (e.g. M1 `f26885c`,
  `7fa7ba1`).
- **Promote** → `docs/m*-promotion.md` gate + `finishing-a-development-branch`
  (merge to `main`, tag `m{n}-complete`).

## Parallel build orchestration (orchestrate-builders)

For larger milestones, builder agents run in **waves** with isolation:

```text
Orchestrator (main session)
  wave 1: explorers   (parallel, main repo, read-only)        ← Observe
  sync barrier
  wave 2: implementers (parallel, one git worktree each)      ← Implement/Test
  sync barrier + merge
  wave 3: integrator  (main repo, full validation)            ← Critic/Test/Promote
```

Hard rules (from the skill):
1. **One file owner per wave** — no overlapping `owned_files` (enforced via
   `file_locks` + `validate-state.sh`).
2. **Implementers always in worktrees** — never parallel edits in the main workspace.
3. **Sync barrier between waves** — never skipped.
4. **Respect `decisions` in STATE** — frozen contracts/ADRs are quoted verbatim to
   each agent; agents must not violate them.
5. **Required checks pass before a packet → `done`.**

The shared bus is `plans/builder/STATE.yaml` (packet status, `decisions`,
`file_locks`, `blockers`, wave). Packets are `plans/builder/packets/*.yaml`
(objective, `owned_files`, `depends_on`, `do_not_touch`, `invariants`,
`required_checks`, `done_criteria`).

## Non-negotiable workflow rules
- **Contract-First (ADR-0001):** no feature code before its spec/contracts are frozen.
- **TDD:** red → green → commit; frequent commits; DRY; YAGNI.
- **Evidence before assertions:** never claim "done/passing" without running the
  command and showing output (this is why gates are evidence-backed, ADR-0010).
- **Additive over breaking:** extend frozen contracts; supersede via a new ADR if you
  must change one.
- **Zero feature debt at a gate:** only intentional `NotImplementedError`/`501`
  stubs with milestone references are allowed.
