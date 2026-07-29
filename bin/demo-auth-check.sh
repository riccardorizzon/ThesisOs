#!/usr/bin/env bash
# ADR-0048 verification — default open; optional token gate when configured.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

API="${THESISOS_API:-http://localhost:8000}"
fail=0

ok() { echo "  OK  $*"; }
bad() { echo "  FAIL $*" >&2; fail=1; }

echo "=== demo-auth-check ==="

echo "--- Artifacts ---"
for f in \
  decisions/ADR-0048-access-control-beta.md \
  backend/app/middleware/beta_access.py \
  frontend/lib/apiAuth.ts \
  frontend/middleware.ts; do
  if [[ -f "$f" ]]; then ok "$f"; else bad "$f missing"; fi
done

if rg -q 'BetaAccessMiddleware' backend/app/main.py 2>/dev/null; then
  ok "middleware wired in main.py"
else
  bad "BetaAccessMiddleware not in main.py"
fi

echo "--- Unit tests ---"
if [[ -f backend/tests/test_beta_access_middleware.py ]]; then
  ok "test_beta_access_middleware.py present"
else
  bad "middleware tests missing"
fi

echo "--- Live default (token unset on running stack) ---"
health="$(curl -s -o /dev/null -w '%{http_code}' "${API}/health" || echo 000)"
projects="$(curl -s -o /dev/null -w '%{http_code}' "${API}/projects" || echo 000)"
if [[ "$health" == "200" ]]; then ok "GET /health → 200"; else bad "GET /health → $health"; fi

# When operator has not set BETA_ACCESS_TOKEN on the container, /projects is open.
# If token IS set in this shell but not on server (or vice versa), report carefully.
if [[ -z "${BETA_ACCESS_TOKEN:-}" ]]; then
  if [[ "$projects" == "200" ]]; then
    ok "GET /projects → 200 (default open DX — token unset locally)"
  elif [[ "$projects" == "401" ]]; then
    bad "GET /projects → 401 but BETA_ACCESS_TOKEN unset in this shell — server has a token; export it to verify"
  else
    bad "GET /projects → $projects"
  fi
else
  denied="$(curl -s -o /dev/null -w '%{http_code}' "${API}/projects" || echo 000)"
  allowed="$(curl -s -o /dev/null -w '%{http_code}' \
    -H "X-Beta-Token: ${BETA_ACCESS_TOKEN}" "${API}/projects" || echo 000)"
  if [[ "$denied" == "401" ]]; then ok "without token → 401"; else bad "without token → $denied (expected 401)"; fi
  if [[ "$allowed" == "200" ]]; then ok "with X-Beta-Token → 200"; else bad "with token → $allowed (expected 200)"; fi
fi

echo "--- FE access model UI ---"
if rg -q 'access-model-panel|Accesso \(beta\)' frontend/app/settings/page.tsx 2>/dev/null; then
  ok "Settings access-model panel present"
else
  bad "Settings access-model panel missing"
fi

echo
if [[ "$fail" -eq 0 ]]; then
  echo "demo-auth-check: PASS"
else
  echo "demo-auth-check: FAIL" >&2
fi
exit "$fail"
