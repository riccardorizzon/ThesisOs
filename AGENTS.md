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

ASEP (ADR-0026) is the overall governance framework. Within it, the **Runtime Platform**
is governed by:

1. **Runtime Constitution** (`docs/runtime-constitution.md`) — architectural invariants of the Runtime Platform (C1–C8); ADRs + plans must stay consistent; changes only via ADR + version bump
2. **ADRs** (`decisions/`) — architectural decisions; must remain consistent with the Constitution
3. **Runtime contract** (`docs/runtime-contract.md`) — onboarding + extension points
4. **Plans / work orders** (`plans/`) — delivery scope
5. **Architecture Decision Checklist** (`docs/architecture-decision-checklist.md`) — per-PR review gate

**Taxonomy (ADR-0026 unchanged):** ASEP is the whole ecosystem. The **Runtime Platform**
(Event Bus, contracts, lifecycle, observability) is the M5 subsystem of ASEP governed by
the Constitution + ADR-0030 (§0).

**Milestone execution:** Run Runtime Platform milestones via the `asep` skill
(`.cursor/skills/asep/SKILL.md`) — e.g. `ASEP: implementa M5.4B`. It loads governance,
builds the Work Order, runs Observe→…→Report, enforces the Constitution, and stops on any
violation. Operational templates live in `.asep/`.

## Review norms

- **Review order (Constitution C7):** Constitution → Layer → Contracts → Events → Feature → Performance → Code
- Every PR touching `backend/app/` declares its layer: Business | Runtime | Infrastructure (ADR-0030 §4)
- Smallest correct diff; match surrounding style
- Never claim tests pass without running them
- Respect `decisions` in STATE.yaml verbatim
