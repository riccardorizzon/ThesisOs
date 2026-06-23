# ThesisOS — M0 Deploy & Promotion Runbook (T11 / T12)

This runbook covers the steps that require **your** machine tooling and **your** GCP
credentials, which the build agent cannot perform for you (it cannot install a local Docker
daemon, authenticate as you, or create/pay for a GCP project).

Everything else in M0 (T0–T10 + hardening) is already authored, reviewed, and committed on
branch `m0-foundations`, with backend tests green (`7/7`), `terraform validate` passing, and
the frontend build passing.

---

## 0. Prerequisites to install

```bash
# Terraform is already installed (v1.15). Install the rest:
brew install --cask google-cloud-sdk     # gcloud
brew install colima docker docker-compose # a Docker runtime without Docker Desktop
colima start                              # starts the Docker VM
docker version                            # confirm the daemon is reachable
```

You also need a **GCP project with billing enabled** and the `Owner` (or equivalent) role.

---

## 1. Local dev verification (Task 8 — `docker compose`)

```bash
cd "/Users/ricky/agent thesis"
cp .env.example .env            # local defaults are fine
docker compose up --build       # builds db (pgvector/pg16), backend, frontend
```
Then verify:
```bash
curl -s localhost:8000/health   # -> {"status":"ok"}
curl -s localhost:8000/ready    # -> {"status":"ready","db":true,"config":true}  (db reachable)
open http://localhost:3000       # Next.js shell, redirects to /chat
```
The backend container runs `alembic upgrade head` on start, so this is also the first real
verification that the migration applies against Postgres + creates the `vector` extension.

**Gate item satisfied when:** `docker_compose: green` and `db_migrations: green` locally.

---

## 2. GCP authentication

```bash
gcloud auth login
gcloud auth application-default login      # ADC for Terraform + local Vertex use
gcloud config set project <YOUR_PROJECT_ID>
```

---

## 3. Provision infrastructure (Task 9 — Terraform)

```bash
cd "/Users/ricky/agent thesis/infra/terraform"
cp terraform.tfvars.example terraform.tfvars
#   edit terraform.tfvars: set project_id, and a db_password (do NOT commit this file)
terraform init
terraform plan -out tfplan
terraform apply tfplan
```
This creates: Artifact Registry repo `thesisos`, Cloud SQL `db-f1-micro` (POSTGRES_16) + db +
user, 4 buckets (documents/exports/temp/logs), Secret Manager secrets (`database-url`,
`vertex-config`), the `thesisos-run` service account + IAM, and the two Cloud Run services.

**Gate item satisfied when:** `terraform_apply: success`.

> ⚠️ **Security decision (do before M1).** The Terraform currently grants
> `roles/run.invoker` to `allUsers`, i.e. the Cloud Run services are **publicly invokable**.
> For M0 (only `/health` exists) this is harmless, but since ThesisOS has **no application
> auth** (ADR-0001, single-user), a public backend at M1+ means anyone with the URL can use
> your assistant and burn Vertex credits. Before M1, lock it down: remove the
> `allUsers` `google_cloud_run_v2_service_iam_member` blocks in `cloudrun.tf` and front the
> app with **IAP** or authenticated-invoker + an identity token. Re-`apply` after.

---

## 4. Build, push, deploy (Task 10 — Cloud Build → Cloud Run)

First grant the Cloud Build service account the roles it needs (documented at the top of
`infra/ci/cloudbuild.yaml`):
```bash
PROJECT_NUMBER=$(gcloud projects describe <YOUR_PROJECT_ID> --format='value(projectNumber)')
CB_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
for ROLE in roles/run.admin roles/artifactregistry.writer roles/iam.serviceAccountUser; do
  gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> --member="serviceAccount:${CB_SA}" --role="$ROLE"
done
```
Then run the pipeline:
```bash
cd "/Users/ricky/agent thesis"
gcloud builds submit --config infra/ci/cloudbuild.yaml --substitutions=_REGION=europe-west1 .
```

**Gate item satisfied when:** `cloud_run: deployed`.

### 4a. Wire the backend to Cloud SQL + secrets (deferred from M0 scaffolding)
The committed Cloud Build deploy steps are intentionally minimal. For a working backend, redeploy with the DB + Vertex wiring:
```bash
SQL_CONN=$(terraform -chdir=infra/terraform output -raw sql_connection_name)
# store the runtime DSN (Cloud SQL unix socket form) in the secret, then mount it:
printf 'postgresql+psycopg://thesisos:<DB_PASSWORD>@/thesisos?host=/cloudsql/%s' "$SQL_CONN" \
  | gcloud secrets versions add database-url --data-file=-

gcloud run services update thesisos-backend --region europe-west1 \
  --add-cloudsql-instances "$SQL_CONN" \
  --set-secrets "DATABASE_URL=database-url:latest" \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=<YOUR_PROJECT_ID>,VERTEX_LOCATION=europe-west1"
```

### 4b. Frontend API URL (build-time caveat)
`NEXT_PUBLIC_API_BASE_URL` is inlined at **build time**, but `docker/frontend.Dockerfile` does
not yet declare it as an `ARG`. To point the frontend at the deployed backend you must (M1
follow-up): add `ARG NEXT_PUBLIC_API_BASE_URL` + `ENV ...` before `npm run build` in the
frontend Dockerfile, then pass `--build-arg NEXT_PUBLIC_API_BASE_URL=$(backend Cloud Run URL)`.
For M0 promotion (health only) this is not required.

---

## 5. Apply migrations on Cloud SQL

Option A — via the Cloud SQL Auth Proxy from your machine:
```bash
SQL_CONN=$(terraform -chdir=infra/terraform output -raw sql_connection_name)
cloud-sql-proxy "$SQL_CONN" &           # listens on 127.0.0.1:5432
cd backend && . .venv/bin/activate
DATABASE_URL="postgresql+psycopg://thesisos:<DB_PASSWORD>@127.0.0.1:5432/thesisos" alembic upgrade head
alembic current                          # expect: 0001_initial (head)
```
(If `docker compose up` in step 1 already ran migrations locally, this is the prod equivalent.)

**Gate item satisfied when:** `db_migrations: green` and `alembic current == 0001_initial`.

---

## 6. Verify health in production

```bash
BACKEND_URL=$(terraform -chdir=infra/terraform output -raw backend_url)
curl -s "$BACKEND_URL/health"            # -> {"status":"ok"}
curl -s "$BACKEND_URL/ready"             # -> db:true once 4a wiring is done
```

**Gate item satisfied when:** `health: green`.

---

## 7. Task 12 — M0 promotion gate

Fill `docs/m0-promotion.md` and only start M1 when ALL are true (ADR-0010):
```yaml
architecture: approved        # docs/architecture.md reviewed
contracts: frozen             # contracts/ + decisions/ committed, unchanged
adr: complete                 # decisions/ has ADR-0001..0010  ✅ done
terraform_apply: success      # step 3
docker_compose: green         # step 1
cloud_run: deployed           # step 4
health: green                 # step 6
db_migrations: green          # step 5 (alembic current == 0001_initial)
zero_feature_debt: true       # only NotImplementedError stubs; no half-built feature  ✅ verified
```
Zero-feature-debt check:
```bash
rg -n "NotImplementedError|wired post-M0|wired in M1" backend/app   # only intentional stubs
```

When green, tag it:
```bash
git tag m0-complete
```

---

## Status legend at handoff
- ✅ Authored + verified locally by the agent: T0–T10, hardening (backend 7/7 tests, terraform validate, frontend build).
- ⏳ Needs you (this runbook): T8 live `compose up`, T11 GCP apply+deploy+migrate, T12 gate.
