# ThesisOS — M0 Deploy & Promotion Runbook (T11 / T12)

This runbook covers the steps that require **your** machine tooling and **your** GCP
credentials, which the build agent cannot perform for you (it cannot install a local Docker
daemon, authenticate as you, or create/pay for a GCP project).

Everything else in M0 (T0–T10 + hardening) is already authored, reviewed, and committed on
branch `m0-foundations`, with backend tests green (`8/8`), `terraform validate` passing, and
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

> ℹ️ **Reproducible apply.** `terraform apply` now succeeds **standalone** before any image is
> built: the Cloud Run services boot from the public placeholder image
> `us-docker.pkg.dev/cloudrun/container/hello`, and a placeholder `database-url` secret version is
> seeded so `secret_key_ref database-url:latest` resolves. Terraform owns the service template but
> **ignores image drift** (`lifecycle.ignore_changes` on the container image), so Cloud Build's
> `gcloud run deploy --image <real>` won't be reverted on the next `apply`. Real rollout order:
> 1. `terraform apply` — infra + placeholder Cloud Run revisions.
> 2. Cloud Build builds/pushes/deploys the **real** images (step 4; Terraform ignores the drift).
> 3. Seed the **real** `DATABASE_URL` secret version (step 4a) so `latest` is the production DSN.
> 4. Run `alembic upgrade head` via the Cloud SQL proxy (step 5).
> 5. Verify `/health` + `/ready` (step 6).

**Gate item satisfied when:** `terraform_apply: success`.

> ✅ **Security posture (locked down by default).** Public access is **OFF by default**
> (`allow_public_invoker = false`): the Cloud Run services are deployed **private /
> authenticated-invoker only**, so no `allUsers` `roles/run.invoker` binding is created. This
> matters because ThesisOS has **no application auth** (ADR-0001, single-user), so a public
> backend at M1+ would let anyone with the URL use your assistant and burn Vertex credits. To
> expose the services publicly (**discouraged — prefer IAP**), set `allow_public_invoker = true`
> in `terraform.tfvars` and re-`apply`. No manual edit of `cloudrun.tf` is needed.

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

### 4a. Seed the real `DATABASE_URL` secret version
The Cloud SQL volume mount, the `DATABASE_URL` secret env (`database-url:latest`), and the Vertex
env (`GOOGLE_CLOUD_PROJECT`, `VERTEX_LOCATION`) are **now wired in Terraform** on the backend
service — no manual `gcloud run services update` is needed. Terraform only seeds a *placeholder*
secret version, so the one remaining step is to add the **real** DSN as a new version (which
becomes `latest`) and re-run the build/deploy so the next revision picks it up:
```bash
SQL_CONN=$(terraform -chdir=infra/terraform output -raw sql_connection_name)
# store the runtime DSN (Cloud SQL unix socket form) as the new `latest` version:
printf 'postgresql+psycopg://thesisos:<DB_PASSWORD>@/thesisos?host=/cloudsql/%s' "$SQL_CONN" \
  | gcloud secrets versions add database-url --data-file=-

# re-run the pipeline (step 4) so the new revision reads the real secret version:
gcloud builds submit --config infra/ci/cloudbuild.yaml --substitutions=_REGION=europe-west1 .
```
Then apply migrations against Cloud SQL (step 5).

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
> **Telemetry note.** The backend now uses real OpenTelemetry (a `TracerProvider` + exporter is
> configured in code), so the `telemetry: green` gate item is satisfied by the code itself.

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
- ✅ Authored + verified locally by the agent: T0–T10, hardening (backend 8/8 tests, terraform validate, frontend build).
- ⏳ Needs you (this runbook): T8 live `compose up`, T11 GCP apply+deploy+migrate, T12 gate.
