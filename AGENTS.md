# AGENTS.md — ThesisOS / ASEP

Conventions for AI coding agents (Cursor, Claude Code) building this repo.

## Build & test

```bash
make install          # backend venv + frontend deps
make ci               # full gate (lint, typecheck, unit, drift, scope, isolation)
make unit-builder-engine   # ASEP Engineering Runtime tests
make up               # docker compose (db, backend, frontend)
```

## Builder orchestration (ASEP)

| Task | Command / skill |
|------|-----------------|
| Observe state | `builder-engine observe --repo-root .` |
| Evaluate policies | `builder-engine policy --repo-root .` |
| Build plan | `builder-engine plan --repo-root .` |
| Cycle preflight | `builder-engine cycle --dry-run --repo-root .` |
| Tail events | `builder-engine events --tail 20 --repo-root .` |
| Validate graph | `builder-engine lint-graph --repo-root .` |
| Dispatch wave | `orchestrate builders wave` (skill) |
| Sync barrier | `orchestrate builders sync` |
| Checker | `.cursor/agents/loop-verifier.md` |
| State bus | `plans/builder/STATE.yaml` |

## Architecture boundaries

- **Product Plane:** `backend/app/`, `frontend/` — runtime LangGraph, chat, RAG
- **Engineering Runtime:** `builder_engine/` — must **not** import `backend.app`
- **Builder agents:** Cursor Task agents; not called at product runtime (ADR-0002)

## Workflow

Contract-first → TDD red/green → evidence-backed gates. See `knowledge/development/workflow.md`.

## Loop engineering

- Config: `LOOP.md`, `STATE.md` (bridge), `loop-budget.md`, `loop-run-log.md`
- Safety: `docs/safety.md`
- Audit: `npx @cobusgreyling/loop-audit . --suggest`

## Governance hierarchy

**Platform investment contract:** `docs/platform-justification.md` — validated value,
hypotheses, exit criteria, scope. Classification registry: `.asep/registry/platform-classification.yaml`
(CI: `make validate-platform-classification`; **not** read by product runtime).

ASEP (ADR-0026) is the overall governance framework.

**Engineering Program** (`docs/engineering-program.md`, `.asep/programs/`) sits between
ASEP and WorkOrders: it binds a domain track (e.g. thesis-agent migration) to capability
roadmaps, OR/E2E done criteria, and release rules — without duplicating Constitution or
runbook content.

Within ASEP, the **Runtime Platform** is governed by:

1. **Runtime Constitution** (`docs/runtime-constitution.md`) — architectural invariants of the Runtime Platform (C1–C8); ADRs + plans must stay consistent; changes only via ADR + version bump
2. **ADRs** (`decisions/`) — architectural decisions; must remain consistent with the Constitution
3. **Runtime contract** (`docs/runtime-contract.md`) — onboarding + extension points
4. **Plans / work orders** (`plans/`) — delivery scope
5. **Architecture Decision Checklist** (`docs/architecture-decision-checklist.md`) — per-PR review gate

**Taxonomy (ADR-0026 unchanged):** ASEP is the whole ecosystem. The **Runtime Platform**
(Event Bus, contracts, lifecycle, observability) is the M5 subsystem of ASEP governed by
the Constitution + ADR-0030 (§0).

**Milestone execution:** Run governed work via the `asep` skill
(`.cursor/skills/asep/SKILL.md`):

- Runtime Platform: e.g. `ASEP: implementa M5.4B` → `runtime-platform.yaml`
- Thesis-agent migration: e.g. `ASEP: esegui OR-1 thesis-agent` → Engineering Program +
  `thesis-agent-migration.yaml`

The skill loads governance, builds the Work Order, runs Observe→…→Report, and stops on
any violation. Pipeline templates live in `.asep/`.

### Architect API

The operator authorizes program execution with a single command — no briefing prompt:

```text
AUTHORIZE PX-3
```

Equivalent: `AUTHORIZE PROGRAM PX-3`, `ASEP: AUTHORIZE PX-3`, or a structured
`# ARCHITECT AUTHORIZATION` block. ASEP interprets this as:

1. Load Program Graph
2. Run pre-flight validation
3. Select first executable EWO
4. Begin implementation (product-only for conformance programs)
5. Update authorization receipt and Conformance Log

Resolver: `.asep/resolvers/authorize.md`. Stable interface — today skill + agent;
tomorrow Engineering Runtime.

## PX-3 Conformance Program (product under SoR contract)

PX-3 is the first **Runtime Conformance Program** — implement product only; MB2 Runtime
is **not authorized**. Start a PX-3 session with:

```text
AUTHORIZE PX-3
```

Enable `.cursor/rules/px3-conformance-program.mdc` when the authorize pipeline selects
PX-3. Record deviations (I/S/A/N) in `.asep/reports/PX3-CONFORMANCE-LOG.md`. Do not modify SoR or governance unless instructed.

## Review norms

- **Review order (Constitution C7):** Constitution → Layer → Contracts → Events → Feature → Performance → Code
- Every PR touching `backend/app/` declares its layer: Business | Runtime | Infrastructure (ADR-0030 §4)
- Smallest correct diff; match surrounding style
- Never claim tests pass without running them
- Respect `decisions` in STATE.yaml verbatim
