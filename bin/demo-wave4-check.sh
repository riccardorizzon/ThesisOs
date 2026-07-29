#!/usr/bin/env bash
# Wave 4 demo gate — growth track: research canvas, cohort pack, GCP deploy doc, auth defer.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

FE="${THESISOS_FE:-http://localhost:3000}"
fail=0

ok() { echo "  OK  $*"; }
bad() { echo "  FAIL $*" >&2; fail=1; }

echo "=== demo-wave4-check ==="

echo "--- Growth docs ---"
for f in \
  docs/demo/DEMO-GROWTH-PLAN.md \
  docs/demo/DEMO-DEPLOY-GCP.md \
  .asep/reports/BETA-COHORT-INVITE.md; do
  if [[ -f "$f" ]]; then
    ok "$f present"
  else
    bad "$f missing"
  fi
done

if rg -q 'Defer M8|defer.*M8|single-user' docs/demo/DEMO-GROWTH-PLAN.md 2>/dev/null; then
  ok "auth defer documented in DEMO-GROWTH-PLAN"
else
  bad "auth defer not documented"
fi

echo "--- Cohort tracker ---"
if [[ -f .asep/reports/THESISOS-v2.0.0-rc.2-BETA-VALIDATION.md ]]; then
  slots="$(rg -c '^\| [0-9]+ \|' .asep/reports/THESISOS-v2.0.0-rc.2-BETA-VALIDATION.md 2>/dev/null || echo 0)"
  if [[ "${slots:-0}" -ge 10 ]]; then
    ok "beta cohort table has ${slots} slots (>= 10)"
  else
    bad "beta cohort table has ${slots} slots (expected >= 10)"
  fi
else
  bad "THESISOS-v2.0.0-rc.2-BETA-VALIDATION.md missing"
fi

echo "--- Research canvas smoke ---"
for path in /research /research/canvas; do
  code="$(curl -s -o /dev/null -w '%{http_code}' "${FE}${path}" || echo 000)"
  if [[ "$code" == "200" ]]; then
    ok "frontend ${path} → 200"
  else
    bad "frontend ${path} → $code"
  fi
done

echo "--- Terraform deploy path ---"
if [[ -f infra/terraform/cloudrun.tf && -f infra/terraform/outputs.tf ]]; then
  ok "infra/terraform Cloud Run stack present"
else
  bad "infra/terraform incomplete"
fi

echo
if [[ "$fail" -eq 0 ]]; then
  echo "demo-wave4-check: PASS"
else
  echo "demo-wave4-check: FAIL" >&2
fi
exit "$fail"
