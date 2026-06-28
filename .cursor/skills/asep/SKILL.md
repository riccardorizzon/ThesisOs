---
name: asep
description: >-
  Run a ThesisOS Runtime Platform milestone end to end from a one-line request
  (e.g. "ASEP: implementa M5.4B" or "Implementa M8.3 Memory Snapshot"). Loads the
  Runtime Constitution, ADRs, Runtime Contract and plan; builds the Work Order;
  executes the ASEP cycle (Observe → Analyze → Strategy → Execute → Verify →
  Commit → Report); enforces layer/contract/event discipline; stops and reports on
  any violation or red gate instead of implementing. Use when asked to start,
  develop, or implement a milestone/phase, or when the user invokes "ASEP".
user_invocable: true
triggers:
  - asep
  - implementa milestone
  - start milestone
  - develop milestone
  - runtime platform milestone
argument-hint: "<phase> [objective]   e.g. M5.4B  or  M8.3 Memory Snapshot"
---

# ASEP — Runtime Platform milestone runner

Technical project manager for the ThesisOS Runtime Platform. Turns a one-line
request into a governed, repeatable milestone: it reads the rules, builds the Work
Order, runs the ASEP cycle, enforces architecture, and reports. **It is process
automation — it does not invent scope.**

**Arguments:** $ARGUMENTS — a phase id (`M5.4B`) and optional objective. If only a
phase is given, deduce the objective from the plan.

## Guards (read first)

- **Not plan mode.** This skill writes code and commits. Exit plan mode first.
- **Governance > skill.** The Runtime Constitution and ADRs override anything here.
- **STOP, don't improvise.** On any stop condition below, produce a report and halt —
  do not implement, do not expand scope, do not weaken a gate.
- **Never modify `git config`.** Commit with inline author override:
  `git -c user.name="ThesisOS Agent" -c user.email="agent@thesisos.local"`.

## Progress checklist

```
- [ ] 1. Parse request → phase + objective
- [ ] 2. Load governance + plan (mandatory reads)
- [ ] 3. Determine milestone scope + baseline
- [ ] 4. Build internal Work Order
- [ ] 5. Pre-flight STOP gate
- [ ] 6. Execute ASEP cycle
- [ ] 7. Verify gates
- [ ] 8. Update documentation
- [ ] 9. Commit
- [ ] 10. Report
```

---

## 1. Parse request

Extract `<phase>` (e.g. `M5.4B`) and `<objective>`. If objective is missing, it
will come from the plan in step 3. Accepts `ASEP: implementa <phase>`,
`Implementa <phase> <objective>`, or `phase: ... / objective: ...`.

## 2. Load governance + plan (mandatory reads)

Read before doing anything else (single source of truth):

1. `docs/runtime-constitution.md` — invariants C1–C8
2. `decisions/ADR-0030-agent-runtime-layer-boundaries.md` — layers R1–R8, event model, taxonomy
3. Any ADR the milestone touches (e.g. ADR-0027 topology, ADR-0014 RunContext, ADR-0007 GraphState)
4. `docs/runtime-contract.md` — extension points + stability
5. `docs/architecture-decision-checklist.md` — review gate
6. The active plan (`plans/*.md`) — locate the phase, its scope, out-of-scope, promotion criteria
7. Frozen-milestones table in the plan — baseline commit; `git log --oneline -5` — last commit + clean tree

## 3. Determine milestone scope + baseline

From the plan phase entry, extract: objective, in-scope files/contracts, out-of-scope,
constraints, acceptance/promotion criteria. Confirm baseline = last commit on branch
and the prior milestone is frozen.

## 4. Build internal Work Order

Fill `.asep/work-order-template.md` in your head/notes from the plan. Do not ask the
user to confirm it unless scope is genuinely ambiguous or conflicts with governance.

## 5. Pre-flight STOP gate

**Do not implement** if any of these hold — instead write the report (step 10, with
`Milestone Status: STOP`) and halt:

- Constitution violation required to satisfy the request (C1–C8)
- Request needs an incompatible public-contract change with no ADR (C5)
- Correct placement would force a cross-layer dependency (C1/C2/C8)
- Request belongs to a layer the milestone forbids (e.g. Business emitting events — R8/C3)
- Working tree dirty, branch wrong, or prior milestone not committed
- `make ci` already red on baseline
- Plan/ADR are inconsistent with the request (e.g. scope not in plan)

## 6. Execute ASEP cycle

```
Observe → Analyze → Strategy → Execute → Verify → Commit → Report
```

- **Observe/Analyze/Strategy:** map scope to files; pick smallest correct diff; respect
  layer membership (ADR-0030 §2) and extension points (runtime-contract §5).
- **Execute (TDD where practical):** implement only in-scope artifacts. Enforce hard rules:
  - Business is pure (C3): no DB/telemetry/logging/event-bus/LangGraph imports in agents.
  - Composition root wires concretes (C2); nodes take injected ports/hooks (R1–R2).
  - Runtime emits canonical events only; Event Bus/subscribers depend on interfaces, never
    concretes; zero-subscriber runtime stays valid (C4/R6/R8).
  - M4 execution node bodies stay frozen unless ADR-authorized (C6).
- Add the tests named in the Work Order (model validity, behavior, regression, purity).

## 7. Verify gates

Run and require green before committing:

```bash
make ci
make unit-m4-recovery
```

Plus the milestone's own unit/behavior tests. If red and not trivially fixable within
scope → STOP and report (do not weaken tests).

## 8. Update documentation

Only what the change requires:
- Plan frozen-milestones table: add this milestone commit + baseline note (after commit, amend or follow-up commit).
- `docs/runtime-contract.md` if events or Runtime API changed.
- `knowledge/architecture/graph.md` if topology changed.

## 9. Commit

One milestone commit (or a small follow-up for the plan baseline record). Conventional
message `feat(<phase>): ...` / `docs(...)`. Author override only (never `git config`).

## 10. Report

Use `.asep/report-template.md`. Always include the status block:

```text
Milestone Status: PASS | STOP
Repository Status: <branch> @ <sha>, working tree clean, merge-ready
Remaining Scope: <next milestone>
Known Risks: <...>
Recommended Next Action: <...>
Readiness <next milestone>: <...>
```

For `STOP`, give the exact stop condition and the smallest change (often an ADR) that
would unblock it. **Never report PASS without having run the gates in step 7.**

---

## Notes

- Works for any future milestone (`M8.3 Memory Snapshot`, etc.) — the process is
  milestone-agnostic; the plan supplies the specifics.
- Templates: `.asep/work-order-template.md`, `.asep/review-template.md`,
  `.asep/report-template.md`, `.asep/promotion-template.md`.
- This skill is the ASEP **operator surface** for the Product Plane Runtime Platform;
  it does not drive `builder_engine` (that is `orchestrate-builders`).
