#!/usr/bin/env bash
# Bootstrap a single GCP dev VM for ThesisOS (the Remote-SSH "lab").
# Run from your Mac (gcloud installed) or Cloud Shell. Safe to re-run.
#
# This is dev/ops tooling, NOT product code and NOT ASEP. It provisions the
# environment where you build ThesisOS; production stays Cloud Run + Cloud SQL.
set -euo pipefail

PROJECT_ID="${PROJECT_ID:?export PROJECT_ID first (e.g. export PROJECT_ID=thesisos-prod)}"
ZONE="${ZONE:-europe-west1-b}"
VM_NAME="${VM_NAME:-thesisos-dev}"
MACHINE_TYPE="${MACHINE_TYPE:-e2-standard-4}"   # no GPU: Vertex does the heavy compute (ADR-0002)
DISK_GB="${DISK_GB:-60}"
SA_NAME="${SA_NAME:-thesisos-dev-vm}"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud config set project "$PROJECT_ID" >/dev/null

echo "==> Enabling APIs (aiplatform, compute)"
gcloud services enable aiplatform.googleapis.com compute.googleapis.com

echo "==> Service account ${SA_EMAIL} (Vertex AI User → ADC via metadata, no key files)"
gcloud iam service-accounts create "$SA_NAME" --display-name="ThesisOS dev VM" 2>/dev/null || true
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/aiplatform.user" --condition=None >/dev/null

STARTUP="$(mktemp)"
cat >"$STARTUP" <<'EOS'
#!/bin/bash
set -e
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y git make python3-venv curl
command -v docker >/dev/null 2>&1 || curl -fsSL https://get.docker.com | sh
EOS

echo "==> Creating VM ${VM_NAME} (${MACHINE_TYPE}, ${DISK_GB}GB) in ${ZONE}"
gcloud compute instances create "$VM_NAME" \
  --zone="$ZONE" \
  --machine-type="$MACHINE_TYPE" \
  --image-family=ubuntu-2404-lts --image-project=ubuntu-os-cloud \
  --boot-disk-size="${DISK_GB}GB" --boot-disk-type=pd-balanced \
  --service-account="$SA_EMAIL" --scopes=cloud-platform \
  --metadata-from-file=startup-script="$STARTUP"
rm -f "$STARTUP"

echo "==> Writing SSH config entries (for Cursor Remote-SSH)"
gcloud compute config-ssh >/dev/null

cat <<EOF

VM ready. SSH host alias: ${VM_NAME}.${ZONE}.${PROJECT_ID}

Next steps:
  1) Cursor → Remote-SSH → connect to "${VM_NAME}.${ZONE}.${PROJECT_ID}"
  2) one-time on the VM:  sudo usermod -aG docker \$USER && exec newgrp docker
  3) git clone <your-repo> && cd "agent thesis"
  4) make install && make up
  5) Forward ports 8000 (backend) and 3000 (frontend) over the SSH session
  6) Real Gemini: set GOOGLE_CLOUD_PROJECT=${PROJECT_ID} in backend/.env

Cost discipline (single-user): STOP the VM when idle —
  gcloud compute instances stop ${VM_NAME} --zone=${ZONE}
EOF
