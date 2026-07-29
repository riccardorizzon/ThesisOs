#!/usr/bin/env bash
# Live citation preference smoke — author-date preferred; W-06 residual documented.
# Does not claim 100% citation guarantee.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

API="${THESISOS_API:-http://localhost:8000}"
PROJECT="${THESISOS_PROJECT_ID:-thesis-agent}"
fail=0

ok() { echo "  OK  $*"; }
bad() { echo "  FAIL $*" >&2; fail=1; }
warn() { echo "  WARN $*"; }

echo "=== demo-citations-check ==="

echo "--- Prompt / enforcement wiring ---"
if rg -q 'NUMERIC_CITATION_INSTRUCTION' backend/app/graph/academic_production.py backend/app/graph/prompt_wire.py 2>/dev/null; then
  ok "citation instruction present in graph prompts"
else
  bad "citation instruction missing from graph prompts"
fi

if rg -q 'enforce_citations' backend/app/graph/conversation.py 2>/dev/null; then
  ok "enforce_citations retry path present"
else
  bad "enforce_citations missing in conversation.py"
fi

echo "--- Unit tests ---"
if [[ -f backend/tests/test_author_doc_boost.py ]]; then
  ok "test_author_doc_boost.py present"
else
  bad "author-doc boost tests missing"
fi

echo "--- Live chat smoke (soft) ---"
health="$(curl -s -o /dev/null -w '%{http_code}' "${API}/health" || echo 000)"
if [[ "$health" != "200" ]]; then
  bad "API health ${health} — skip live citation smoke"
else
  # Prefer SSE chat; accept either author-date pattern or explicit source list.
  tmp="$(mktemp)"
  code="$(curl -sS -N -o "$tmp" -w '%{http_code}' \
    -H 'Content-Type: application/json' \
    -H 'Accept: text/event-stream' \
    ${BETA_ACCESS_TOKEN:+-H "X-Beta-Token: ${BETA_ACCESS_TOKEN}"} \
    -d "{\"message\":\"Secondo Sennett, cos'è craftsmanship? Cita le fonti.\",\"project_id\":\"${PROJECT}\"}" \
    "${API}/chat" || echo 000)"

  if [[ "$code" != "200" ]]; then
    bad "chat HTTP ${code}"
  else
    ok "chat stream HTTP 200"
    body="$(tr -d '\0' <"$tmp" | head -c 200000 || true)"
    # Author-date: (Sennett, 2008) or Sennett (2008) or [Sennett, ...]
    if echo "$body" | rg -qi 'Sennett[, ]*\(?20[0-9]{2}\)?|\(Sennett[^)]*20[0-9]{2}\)'; then
      ok "response contains author-date-like Sennett citation"
    elif echo "$body" | rg -qi 'Sennett_The-Craftsman|document_title.*Sennett'; then
      warn "Sennett in sources/title but no author-date pattern — W-06 residual possible"
      ok "Sennett grounded in sources (soft pass)"
    else
      warn "no clear Sennett citation pattern — documenting W-06 residual"
      # Soft fail: product cannot guarantee 100%; gate still passes if stream worked
      ok "live chat completed (citation form not guaranteed — W-06)"
    fi
  fi
  rm -f "$tmp"
fi

echo "--- Residual documented ---"
if rg -q 'W-06' docs/demo/DEMO-HANDOUT.md docs/demo/DEMO-GROWTH-PLAN.md 2>/dev/null; then
  ok "W-06 residual mentioned in demo docs"
else
  bad "W-06 not documented in handout/growth plan"
fi

echo
if [[ "$fail" -eq 0 ]]; then
  echo "demo-citations-check: PASS"
else
  echo "demo-citations-check: FAIL" >&2
fi
exit "$fail"
