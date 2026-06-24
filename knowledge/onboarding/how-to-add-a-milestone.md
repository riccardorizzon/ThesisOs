# How to Add / Run a Milestone

> The end-to-end process for taking a roadmap milestone from idea to promoted. Sources: ADR-0001/0010, M0 & M1 specs/plans, `docs/m*-promotion.md`, `.cursor/skills/orchestrate-builders/SKILL.md`, `development/workflow.md`.

A milestone is **one vertical slice** delivered against frozen contracts and closed
by an evidence-backed gate. Follow the AgentOS loop.

## 0. Precondition
The previous milestone is **promoted** (gate green + tag, e.g. `m1-complete`). Do
not start in parallel before the tag — it causes contract drift (ADR-0010).

## 1. Scope (CEO + PM)
- PM writes the milestone's **IS / IS-NOT** lists (anti-goals matter as much as
  goals). Map it to the contracts it must wire (OpenAPI `x-milestone`, agent
  `milestone`, event `milestone`). CEO approves scope.

## 2. Design spec (Architect) — FREEZE
- Author `docs/superpowers/specs/<date>-<milestone>-design.md` with: Context & Goal,
  Scope (IS/IS-NOT), Architecture (how it **extends** the seam), Components &
  Boundaries, Data Flow & Persistence, Contracts (additive), SSE/Errors as needed,
  Testing, **Promotion Criteria (YAML)**, Open Questions/Risks.
- Write any new **ADRs** (additive contract evolution; supersede only via a new ADR).
- Set the spec `Status: Frozen/Approved`.

## 3. Plan (Planner)
- Turn the frozen spec into a TDD task plan (`docs/superpowers/plans/...`): each task
  = files + failing test + impl + passing run + commit.
- For parallel builds, create `plans/builder/packets/*.yaml` + `STATE.yaml`
  (`decisions` = frozen constraints, `owned_files`, `depends_on`, `wave`).
- Self-review: every spec section → a task.

## 4. Implement + Test (Backend/Frontend agents)
- Run the AgentOS loop per task (red→green→commit). Stay in `owned_files`; respect
  STATE `decisions`. Parallel builds use worktrees + waves + sync barriers.
- Extend the graph with new nodes; realize OpenAPI stubs; add events; keep
  `GraphState`/`RunContext`/`TokenChunk` frozen.

## 5. Critic + Revise
- Review subagents (`code-reviewer`, Bugbot) review the merged work; apply fixes as
  new commits (like M1's `f26885c`, `7fa7ba1`).

## 6. QA + Gate (Promotion)
- Make every gate item green with a **reproducible command + observed output**.
- Record evidence in `docs/m{n}-promotion.md` (mirror M0/M1 format: gate YAML +
  Evidence section + known follow-ups).
- Zero feature debt: `rg "NotImplementedError|wired in M..."` shows only intentional
  stubs.

## 7. Promote
```bash
git checkout main
git merge --no-ff m{n}-<name>
git tag m{n}-complete
# release vX.Y.Z-m{n}
```
Use the `finishing-a-development-branch` skill. Only after the tag, start the next.

## 8. Update knowledge
- Update `context/current-state.md`, `context/completed-work.md`,
  `context/next-actions.md`, `project/milestones.md`, `memory/project-memory.md`,
  and any affected `agents/` / `contracts/` / `decisions/` docs.

## Definition of done (per milestone)
- Spec frozen, plan executed, contracts extended additively, gate fully green +
  evidence, branch merged + tagged, knowledge updated, zero feature debt, no frozen
  contract changed without an ADR, nothing from the IS-NOT list shipped.
