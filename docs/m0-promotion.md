# M0 Promotion Gate — Status

_As of 2026-06-24. Local + GCP items verified live on project `thesisos-prod` (see evidence
appendix below and `docs/m0-runbook.md`). Nothing in this file is self-declared: every green
item has a reproducible command + observed output._

```yaml
# --- Verified locally (green) ---
docker_compose: green        # `docker compose up --build`: db(healthy)+backend+frontend, volume pgdata
health:         green        # local backend -> {"status":"ok"}
ready:          green        # local backend -> {"status":"ready","db":true,"config":true}
db_migrations:  green        # alembic 0001_initial on local Postgres 16 + Cloud SQL prod
telemetry:      green        # real OpenTelemetry TracerProvider + env-selected exporter (code + test)
contracts:      frozen       # contracts/ (openapi, 9 agents, events, db schema) committed
adr:            frozen       # decisions/ADR-0001..0010
tests:          8/8 green    # backend pytest (graph_state, models_import, schema_snapshot, system_endpoints, telemetry)
ruff:           green        # ruff check app
drift_tests:    green        # test_schema_snapshot guards models <-> schema.sql
zero_feature_debt: true      # only intentional NotImplementedError / 501 stubs (jobs, events, LLM M1)

# --- GCP (thesisos-prod) — green ---
terraform_apply: success     # Cloud SQL, buckets, secrets, IAM, Cloud Run, APIs (incl. aiplatform)
cloud_run:       deployed    # thesisos-backend + thesisos-frontend (amd64 images in Artifact Registry)
health_cloud:    green       # /health + /ready on Cloud Run (authenticated invoker; no public allUsers)
db_migrations_cloud: green   # alembic 0001_initial on Cloud SQL: 15 tables, pgvector 0.8.1, embeddings=vector(768)
```

## Evidence (verified 2026-06-24)

```text
# Cloud Run (gcloud run services list)
thesisos-backend   https://thesisos-backend-napiaa5loq-ew.a.run.app   READY=True
thesisos-frontend  https://thesisos-frontend-napiaa5loq-ew.a.run.app  READY=True

# Cloud SQL (gcloud sql instances list)
thesisos-pg  POSTGRES_16  RUNNABLE

# Authenticated endpoints (curl -H "Authorization: Bearer $(gcloud auth print-identity-token)")
/health -> {"status":"ok"}
/ready  -> {"status":"ready","db":true,"config":true}
frontend (no token) -> HTTP 403   # private/authenticated-invoker lockdown confirmed

# Cloud SQL schema (psql via cloud-sql-proxy)
public tables = 15: agent_runs, agent_steps, alembic_version, chapters, chunks, citations,
  conversations, documents, embeddings, events, memories, messages, notes, sources, tasks
pg_extension vector = 0.8.1
alembic_version = 0001_initial
embeddings.embedding = vector(768)

# Local (backend/)
pytest -> 8 passed
ruff check app -> All checks passed
terraform validate -> Success
```

## GCP endpoints (private — use identity token)

```bash
BACKEND=$(terraform -chdir=infra/terraform output -raw backend_url)
TOKEN=$(gcloud auth print-identity-token)
curl -H "Authorization: Bearer $TOKEN" "$BACKEND/health"   # {"status":"ok"}
curl -H "Authorization: Bearer $TOKEN" "$BACKEND/ready"      # db:true, config:true
```

| Resource | Value |
|----------|-------|
| Project | `thesisos-prod` |
| Region | `europe-west1` |
| Cloud SQL | `thesisos-pg` / db `thesisos` |
| Backend URL | `terraform output backend_url` |
| Frontend URL | `terraform output frontend_url` |

## Known non-blockers (M1 follow-ups)

- **Cloud Build CI:** `gcloud builds submit` returned PERMISSION_DENIED; images were built with `docker buildx` (linux/amd64) and deployed via `gcloud run deploy`. Re-enable Cloud Build when org policy allows.
- **`vertex-config` secret:** exists but has no version yet — Vertex LLM wiring is M1 (ADR-0002).
- **Frontend → backend URL:** `NEXT_PUBLIC_API_BASE_URL` not wired in prod build (M0 health-only; see runbook §4b).
- **DSN ownership = Terraform.** The real `database-url` DSN is now rendered by Terraform from
  `var.db_password` + the Cloud SQL connection name (`secrets.tf`), so it is the single source of
  truth (no manual `gcloud secrets versions add` needed). Consequence: the DB password lands in
  Terraform **state**. State is local-only and git-ignored (`*.tfstate`), acceptable for this
  single-user thesis; if a remote backend is ever added, it MUST be encrypted (e.g. GCS backend).

## Promotion (only after ALL green)

```bash
git checkout main
git merge --no-ff m0-foundations
git tag m0-complete
# release: v0.0.1-m0
```

Then — and only then — start **M1 (Conversation System)** against the frozen contracts. No
parallel M1 work before `m0-complete` exists (avoid contract drift / architectural debt).
