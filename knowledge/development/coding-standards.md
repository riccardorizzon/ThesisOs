# Coding Standards

> Sources: `backend/pyproject.toml`, M0/M1 plans, `frontend/` config, ADR-0005, observed code in `backend/app/**` and `frontend/**`.

## Languages & versions
- **Backend:** Python ≥ 3.12. **Python everywhere server-side** (backend,
  orchestrator, agents, retrieval) — ADR-0005.
- **Frontend:** TypeScript only, Next.js 15 (App Router) + React 19.
- No TypeScript on the server; no Python in the frontend.

## Python
- **Lint/format:** `ruff` (line-length 100). `ruff check app` must be clean before a
  gate.
- **Types:** type hints throughout; `from __future__ import annotations` where useful;
  modern unions (`str | None`). Pydantic v2 for models/settings.
- **Async:** the streaming/request path is async; use the async DB session
  (`session_async.py`) there to avoid blocking the event loop. `asyncio_mode=auto`
  for tests.
- **Config:** read all runtime config from `core/config.py` `Settings`
  (single source of truth, ADR-0013) — do not read env vars ad hoc.
- **DB:** SQLAlchemy 2.0 typed `Mapped[...]` models; UUID PKs (`gen_random_uuid()`);
  `TIMESTAMP(timezone=True)` defaults `now()`; JSONB for flexible fields; the
  `metadata` column is `metadata_` in Python.
- **Errors:** raise clean, typed errors; return contract `Error{code,message}` to
  clients — **never** stack traces (M1 spec §8). Log with `logger.exception`.
- **Stubs:** unimplemented surfaces raise `NotImplementedError("… wired in M{n}")` or
  return `501` — never silent no-ops.

## TypeScript / React
- `npx tsc --noEmit` clean; `next build` green before a gate.
- Tailwind for styling; Zustand for client state (no heavier state lib).
- SSE parsing must be CRLF-safe and frame-boundary-correct.
- Keep non-milestone routes as empty placeholders.

## Comments
- Comment **intent/trade-offs/constraints**, not narration. The codebase's good
  examples explain *why* (e.g. "usage carried via custom stream to keep GraphState
  frozen"), not *what*.

## Contracts discipline
- Extend frozen contracts **additively**; never change `GraphState`, domain DB
  models, or accepted ADRs without a **new ADR**.
- `RunContext` (execution) and `GraphState` (domain) never mix.
- `TokenChunk` stays exactly 3 fields.

## Commits
- Conventional, scoped to the milestone: `feat(m1): …`, `fix(m1): …`,
  `contracts(m1): …`, `docs(m1): …`, `build(m1): …`, `chore(m1): …`.
- TDD cadence: red → green → **commit**; commit frequently.
- One file owner per wave (parallel builds); stay inside `owned_files`.

## Testing
- TDD: write the failing test first. Backend tests from `backend/` via
  `.venv/bin/python -m pytest`. See `development/testing-strategy.md`.

## Security / safety
- No app auth (single-user) → keep services private (authenticated-invoker) in prod.
- No secrets in git; `*.tfstate`, `.env`, `docker-compose.override.yml` are
  gitignored. Don't commit credentials.
