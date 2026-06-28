# Dev VM — Google Cloud (Remote-SSH lab)

The single development environment for ThesisOS. You code from Cursor on the
Mac; everything runs on this VM. **This is the lab, not production** —
production stays Cloud Run + Cloud SQL (ADR-0004 / ADR-0008). The VM gives you
prod *parity* via the same container images (`docker-compose.yml`), so there is
no environment drift and nothing to migrate when you do deploy.

> Operational tooling only. Not product code, not ASEP.

## Prerequisites

- `gcloud` installed (Mac) or use Cloud Shell.
- A GCP project with billing enabled. Set its id:
  ```bash
  export PROJECT_ID=your-real-project   # NOT the "your-gcp-project" placeholder in terraform.tfvars
  ```

## Bootstrap (one command)

```bash
bash infra/dev-vm/create-vm.sh
```

This enables the Vertex + Compute APIs, creates a service account with
**Vertex AI User** (so the VM authenticates to Vertex via the metadata server —
no key files), creates an `e2-standard-4` Ubuntu VM (no GPU — Vertex does the
heavy compute), installs Docker/git/make, and writes the SSH config for Cursor.

Override any default via env var, e.g. `MACHINE_TYPE=e2-standard-2 bash infra/dev-vm/create-vm.sh`.

## Connect & run

1. Cursor → **Remote-SSH** → host `thesisos-dev.<zone>.<project>`.
2. One-time: `sudo usermod -aG docker $USER && exec newgrp docker`.
3. `git clone <repo> && cd "agent thesis"`.
4. `make install` then `make up` (db + backend + frontend via docker compose).
5. Forward ports **8000** (backend) and **3000** (frontend) over SSH, then open
   `http://localhost:3000`. Do **not** expose the VM publicly for a single-user tool.

## Enable real Gemini

In `backend/.env` (read by `app/core/config.py`):

```env
GOOGLE_CLOUD_PROJECT=your-real-project
VERTEX_LOCATION=europe-west1
```

With `GOOGLE_CLOUD_PROJECT` empty the backend uses the `NotConfiguredLLM` stub
(ADR-0013). The attached service account makes ADC work inside the container.

## Cost discipline (single-user)

- **Stop the VM when you're not working** — you then pay only for the disk:
  ```bash
  gcloud compute instances stop thesisos-dev --zone=europe-west1-b
  gcloud compute instances start thesisos-dev --zone=europe-west1-b
  ```
- Use the `pgvector/pgvector:pg16` **container** for dev (already in
  `docker-compose.yml`) — not Cloud SQL. Cloud SQL is the production database only.
- Do **not** add Redis / centralized monitoring now — that is M11, pulled only on a real product block.

## Teardown

```bash
gcloud compute instances delete thesisos-dev --zone=europe-west1-b
```
