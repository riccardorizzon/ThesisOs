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

## Review norms

- Smallest correct diff; match surrounding style
- Never claim tests pass without running them
- Respect `decisions` in STATE.yaml verbatim
