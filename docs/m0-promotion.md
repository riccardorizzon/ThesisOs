# M0 Promotion Gate — Status

_As of 2026-06-23. Local items verified by the build session; GCP items require your
authenticated, billing-enabled GCP project (see `docs/m0-runbook.md`)._

```yaml
# --- Verified locally (green) ---
docker_compose: green        # `docker compose up --build`: db(healthy)+backend+frontend, volume pgdata
health:         green        # local backend -> {"status":"ok"}
ready:          green        # local backend -> {"status":"ready","db":true,"config":true}
db_migrations:  green        # alembic 0001_initial applied on real Postgres 16:
                             #   15 tables (14 app + alembic_version), pgvector 0.8.3, embeddings.embedding = vector
telemetry:      green        # real OpenTelemetry TracerProvider + env-selected exporter (code + test)
contracts:      frozen       # contracts/ (openapi, 9 agents, events, db schema) committed
adr:            frozen       # decisions/ADR-0001..0010
tests:          8/8 green    # backend pytest (graph_state, models_import, schema_snapshot, system_endpoints, telemetry)
ruff:           green        # ruff check app
drift_tests:    green        # test_schema_snapshot guards models <-> schema.sql

# --- Pending: require YOUR GCP account (runbook) ---
terraform_apply: pending     # `terraform validate` green; `apply` needs auth + billing
cloud_run:       pending     # Cloud Build -> Artifact Registry -> Cloud Run deploy
health_cloud:    pending     # /health on the deployed Cloud Run backend URL
```

## What's left to flip the gate fully green

Run `docs/m0-runbook.md` §2→§6 with your GCP project:
1. `terraform apply` (now reproducible: placeholder hello image + placeholder secret version; public access off by default).
2. Cloud Build builds/pushes/deploys the real images (Terraform ignores image drift).
3. Seed the real `DATABASE_URL` secret version; run `alembic upgrade head` via the Cloud SQL proxy.
4. Confirm `/health` (and `/ready`) on the Cloud Run backend URL.

## Promotion (only after ALL green)

```bash
git checkout main
git merge --no-ff m0-foundations
git tag m0-complete
# release: v0.0.1-m0
```

Then — and only then — start **M1 (Conversation System)** against the frozen contracts. No
parallel M1 work before `m0-complete` exists (avoid contract drift / architectural debt).
