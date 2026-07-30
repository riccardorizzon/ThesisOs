#!/usr/bin/env bash
# AP-001 — SSR Base URL Misconfiguration anti-pattern guard (Recovery Theme A).
# Fails if NEXT_PUBLIC_API_BASE_URL is referenced outside the authorized resolver.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=require-rg.sh
. "$ROOT/bin/require-rg.sh"

SCAN_DIR="${ROOT}/frontend/lib"

violations="$(rg -n "NEXT_PUBLIC_API_BASE_URL" "$SCAN_DIR" --glob '*.ts' --glob '*.tsx' \
  --glob '!apiBase.ts' || true)"

if [[ -n "$violations" ]]; then
  echo "AP-001 FAIL: NEXT_PUBLIC_API_BASE_URL outside frontend/lib/apiBase.ts"
  echo "$violations"
  echo "Use apiBaseUrl() from @/lib/apiBase instead."
  exit 1
fi

echo "AP-001 PASS: no direct NEXT_PUBLIC_API_BASE_URL in frontend/lib (except apiBase.ts)"
