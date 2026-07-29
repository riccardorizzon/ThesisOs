# Deploy GCP — Wave 4 (oltre tunnel Cloudflare)

> **Quando usarlo:** demo stabile multi-giorno, cohort beta remota, URL permanente.  
> **Alternativa rapida:** tunnel `bin/beta-public-open.sh` (Wave 3 runbook).

## Prerequisiti

- Progetto GCP con billing (`GOOGLE_CLOUD_PROJECT`)
- `gcloud` + `terraform` installati
- Secret `database-url` in Secret Manager (connection string Cloud SQL)
- CI deploy via `infra/ci/cloudbuild.yaml` (immagini backend/frontend)

## Terraform (infra esistente)

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Compila: project_id, region, vertex_location, gemini_model, …
terraform init
terraform plan
terraform apply
```

Output attesi (`outputs.tf`):

- `backend_url` — Cloud Run API
- `frontend_url` — Cloud Run UI
- `sql_connection_name` — socket Cloud SQL

## Post-apply checklist

```bash
# 1. Deploy immagini (Cloud Build o manuale)
# Vedi infra/ci/cloudbuild.yaml

# 2. Verifica health
curl -sf "$(terraform output -raw backend_url)/health"

# 3. Frontend → API
curl -sf "$(terraform output -raw frontend_url)/" -o /dev/null -w '%{http_code}\n'

# 4. Gate demo sul nuovo stack (se dati migrati)
THESISOS_API="$(terraform output -raw backend_url)" make demo-gate
```

## Migrazione dati demo

Per cohort beta con corpus curato:

1. `make demo-backup` sul VM sorgente
2. Restore su Cloud SQL target (pg_dump / pg_restore)
3. `make seed-curated-sources` se corpus core mancante
4. `make demo-gate`

## Rollback

- Cloud Run: redeploy immagine precedente via Cloud Build history
- DB: restore da backup Wave 3 (`docs/demo/DEMO-OPS-RUNBOOK.md` § Ripristino)

## Limitazioni attuali

- **Auth:** single-user — nessun login multi-tenant (M8)
- **Tunnel vs GCP:** preferire GCP per cohort >3 giorni; tunnel OK per demo singola
