# Infrastructure Architecture

> Sources: `docs/architecture.md` §8, M0 spec §14, `infra/terraform/*`, `infra/ci/cloudbuild.yaml`, `docker/`, `docker-compose.yml`, `docker-compose.override.yml`, `docs/m0-runbook.md`, `docs/m0-promotion.md`, ADR-0004/0008/0013.

GCP from day one, with **dev/prod parity** via identical container images (ADR-0004,
ADR-0008). Verified live on project **`thesisos-prod`**, region **`europe-west1`**.

## Local (dev)

`docker-compose.yml` runs the same images as prod:
- `db`: `pgvector/pgvector:pg16` (Postgres + pgvector), healthcheck, `pgdata` volume.
- `backend`: FastAPI image; command `alembic upgrade head && uvicorn …`; depends on
  healthy `db`; port 8000.
- `frontend`: Next.js image; port 3000.

`docker-compose.override.yml` (gitignored locally) wires Vertex for the local stack:
`GOOGLE_CLOUD_PROJECT`, `VERTEX_LOCATION`, `GEMINI_MODEL`, and mounts ADC
(`~/.config/gcloud/application_default_credentials.json`) into the backend.

```bash
cp .env.example .env
docker compose up --build
curl localhost:8000/health   # {"status":"ok"}
```

## GCP (prod) — Terraform (`infra/terraform/`)

Files: `versions.tf`, `variables.tf`, `apis.tf`, `artifact_registry.tf`,
`cloudsql.tf`, `secrets.tf`, `storage.tf`, `iam.tf`, `cloudrun.tf`, `outputs.tf`,
`terraform.tfvars(.example)`.

**Provisioned resources:**
- **APIs:** run, sqladmin, secretmanager, storage, artifactregistry, **aiplatform**.
- **Artifact Registry:** Docker repo `thesisos`.
- **Cloud SQL:** Postgres 16 `thesisos-pg` on **`db-f1-micro`** (cheapest
  shared-core tier — do not optimize yet) + database `thesisos` + user. pgvector
  enabled by the Alembic `CREATE EXTENSION`.
- **Secret Manager:** `database-url` (real DSN rendered by Terraform from
  `var.db_password` + Cloud SQL connection name), `vertex-config` (exists but
  **intentionally empty/unused** — ADR-0013).
- **Cloud Storage:** buckets `documents`, `exports`, `temp`, `logs` (uniform access).
- **Cloud Run:** services `thesisos-backend` + `thesisos-frontend`.
- **Service account `thesisos-run`:** `aiplatform.user` + `cloudsql.client` +
  `secretmanager.secretAccessor` + `storage.objectAdmin`.

**Security posture (locked down by default):** `allow_public_invoker = false` →
services are **private / authenticated-invoker only** (no `allUsers`). This matters
because ThesisOS has **no app auth** (ADR-0001), so a public backend would let
anyone burn Vertex credits. Set `allow_public_invoker = true` only to expose
publicly (discouraged — prefer IAP).

**Reproducible apply:** `terraform apply` succeeds standalone — Cloud Run boots from
the public `cloudrun/hello` placeholder and Terraform `ignore_changes` on the
container image so the real `gcloud run deploy` isn't reverted.

## CI/CD (`infra/ci/cloudbuild.yaml`)

Build backend + frontend images → push to Artifact Registry → `gcloud run deploy`
both services. Cloud Build SA needs `run.admin`, `artifactregistry.writer`,
`iam.serviceAccountUser`.

> **Known non-blocker:** in the M0 promotion, `gcloud builds submit` returned
> PERMISSION_DENIED (org policy); images were built with `docker buildx`
> (linux/amd64) and deployed via `gcloud run deploy`. Re-enable Cloud Build when
> org policy allows.

## Deploy / rollout order (from `docs/m0-runbook.md`)

1. `terraform apply` — infra + real `database-url` DSN + placeholder Cloud Run.
2. Cloud Build (or buildx) builds/pushes/deploys real images.
3. `alembic upgrade head` via the Cloud SQL Auth Proxy.
4. Verify `/health` + `/ready` (authenticated identity token).

## Observability (M0/M11)

M0 ships FastAPI OTel instrumentation hook + structured JSON logging +
`prometheus_client` `/metrics`, and a real `TracerProvider` + env-selected exporter
(`telemetry: green`). Full Cloud Trace/Logging exporters + LLM-abstraction tracing
are an **M1/M11** concern.

## Cost & scaling notes (open, scheduled)
- `db-f1-micro`: fine for scaffolding; reassess at M3/M4 (ingestion + embeddings load).
- Cloud Run cold starts: acceptable for single-user; revisit at M11.
- In-process job worker: fine M0–M6; durable queue (Cloud Run Jobs/Cloud Tasks)
  needed before M11 (ADR-0009, spec §19).
- Terraform state holds the DB password and is **local-only + git-ignored**
  (`*.tfstate`); a remote backend MUST be encrypted (e.g. GCS) if ever added.

## Key identifiers (prod)
| Resource | Value |
|----------|-------|
| Project | `thesisos-prod` |
| Region | `europe-west1` |
| Cloud SQL | `thesisos-pg` / db `thesisos` |
| Cloud Run | `thesisos-backend`, `thesisos-frontend` |
| Model | `gemini-2.5-pro` (Vertex), `text-multilingual-embedding-002` |
