#!/usr/bin/env bash
# Post-deploy / weekly ops gate: health, LLM chat, export contract, document audit.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=require-rg.sh
. "$ROOT/bin/require-rg.sh"

fail=0
ok() { echo "  OK  $*"; }
bad() { echo "  FAIL $*"; fail=1; }

# ADR-0048 — forward shared beta token when operator has it in the environment
AUTH_H=()
if [[ -n "${BETA_ACCESS_TOKEN:-}" ]]; then
  AUTH_H=(-H "X-Beta-Token: ${BETA_ACCESS_TOKEN}")
fi

echo "=== ThesisOS ops-check ==="

# Stack
if docker compose ps backend 2>/dev/null | rg -q 'Up'; then
  ok "backend container Up"
else
  bad "backend container not Up (run: make up)"
fi

# Health
if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
  ok "/health"
else
  bad "/health unreachable"
fi

if curl -sf http://localhost:8000/ready | rg -q '"db":true'; then
  ok "/ready (db + config)"
else
  bad "/ready not ready"
fi

# LLM
proj="$(docker compose exec -T backend printenv GOOGLE_CLOUD_PROJECT 2>/dev/null || true)"
if [[ -n "$proj" ]]; then
  ok "GOOGLE_CLOUD_PROJECT=$proj"
else
  bad "GOOGLE_CLOUD_PROJECT empty — copy docker-compose.override.example.yml and set backend/.env"
fi

code="$(curl -s -o /tmp/ops_chat.json -w '%{http_code}' -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' "${AUTH_H[@]}" -d '{"message":"ops ping"}' || echo 000)"
if [[ "$code" == "200" ]]; then
  ok "POST /chat → 200"
else
  bad "POST /chat → $code ($(head -c 120 /tmp/ops_chat.json))"
fi

# Wave C export contract
ex="$(curl -s -o /dev/null -w '%{http_code}' "${AUTH_H[@]}" \
  "http://localhost:8000/export/chapters/00000000-0000-0000-0000-000000000000.md")"
if [[ "$ex" == "422" ]]; then
  ok "export without project_id → 422"
else
  bad "export without project_id → $ex (expected 422 — rebuild backend?)"
fi

# No secrets in image
if docker compose exec -T backend sh -c 'test ! -f /app/.env && test ! -f /app/backend/.env' 2>/dev/null; then
  ok "no .env baked in image"
else
  bad ".env present inside image"
fi

# Document audit summary
echo
if [[ -x bin/audit-document-storage.sh ]]; then
  bash bin/audit-document-storage.sh | rg -n 'Documents in DB|Original on disk|Missing originals|Failed parse' || true
else
  bad "bin/audit-document-storage.sh missing"
fi

echo
if [[ "$fail" -eq 0 ]]; then
  echo "ops-check: PASS"
  exit 0
fi
echo "ops-check: FAIL — see items above"
exit 1
