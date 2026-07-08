# ThesisOS

Single-user research and thesis-writing AgentOS. Runtime LLM: Vertex AI (Gemini +
multilingual embeddings). Storage: Postgres + pgvector. Local stack via Docker;
production target: GCP (Cloud Run + Cloud SQL).

## Status

**Beta — `v2.0.0-rc.2`** — M7 complete on `main`; RC tagged @ `5039df77`.
Beta validation open (7-day window). Onboarding:
[`.asep/reports/RC-BETA-ONBOARDING.md`](.asep/reports/RC-BETA-ONBOARDING.md).

Next: GA approval after beta exit → M8 (new features).

## Product surfaces

| Route | Module | Notes |
|-------|--------|-------|
| `/` | Home | Import CTA, navigation |
| `/sources`, `/sources/upload` | Sources | DB library, upload → index |
| `/knowledge` | Knowledge | DB concepts + search |
| `/writing`, `/writing/[chapterId]` | Writing | Grounded AI panel, export menu |
| `/review` | Review | Proposals API, accept → chapter |
| `/ai` | Chat | Persistent conversations |
| `/research` | Research | Canvas + guided trails |

Legacy paths (`/workspace`, `/chat`, `/library`, `/documents/*`, `/memory/*`,
`/outline`) redirect to the routes above (ADR-0036).

## Layout

- `backend/` — FastAPI app (Python)
- `frontend/` — Next.js app
- `contracts/` — OpenAPI, agent I/O, DB schema, events
- `decisions/` — ADRs
- `plans/` — M7 program plans + dashboard
- `infra/` — Terraform + CI/CD
- `docs/` — architecture + specs

## Local dev

```bash
cp .env.example .env   # GOOGLE_CLOUD_PROJECT, DATABASE_URL, etc.
make install
make ensure-test-db
make ci                # full gate (lint, typecheck, unit, drift, scope)
make up                # docker compose up --build -d
curl localhost:8000/health   # {"status":"ok"}
```

Open `http://localhost:3000`. Backend API: `http://localhost:8000`.

### M7 smoke

```bash
make dogfood-m7        # API workflow + Playwright (requires stack + Vertex ADC for indexing)
```

Playwright only (starts dev servers on 8001/3001):

```bash
cd tests/e2e && npx playwright test m7-product-flow.spec.ts
```

### Useful targets

| Command | Purpose |
|---------|---------|
| `make check` | Fast pre-push gate |
| `make status` | Product / infra snapshot |
| `make down` | Stop Docker stack |

## Governance

ASEP engineering runtime: `builder-engine`, plans in `plans/builder/`. See
[`AGENTS.md`](AGENTS.md) for agent conventions and CI gates.
