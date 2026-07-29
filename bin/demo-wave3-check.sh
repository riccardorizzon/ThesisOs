#!/usr/bin/env bash
# Wave 3 demo gate — ops resilience: runbook, backup, no failed docs, mid-demo smoke.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

API="${THESISOS_API:-http://localhost:8000}"
PROJECT="${THESISOS_PROJECT_ID:-thesis-agent}"
SHOWCASE_ID="503c33f5-a3d8-40ee-adc0-3ff067747a17"
fail=0

ok() { echo "  OK  $*"; }
bad() { echo "  FAIL $*" >&2; fail=1; }

echo "=== demo-wave3-check (project=$PROJECT) ==="

echo "--- Runbook ---"
if [[ -f docs/demo/DEMO-OPS-RUNBOOK.md ]]; then
  ok "DEMO-OPS-RUNBOOK.md present"
else
  bad "docs/demo/DEMO-OPS-RUNBOOK.md missing"
fi

if rg -q '^deploy-backend:' Makefile 2>/dev/null; then
  ok "make deploy-backend target exists"
else
  bad "make deploy-backend missing from Makefile"
fi

if [[ -x bin/demo-backup.sh ]]; then
  ok "bin/demo-backup.sh executable"
else
  bad "bin/demo-backup.sh missing or not executable"
fi

echo "--- Backup ---"
backup=""
if [[ -f /tmp/thesisos-latest-backup.env ]]; then
  # shellcheck disable=SC1091
  source /tmp/thesisos-latest-backup.env
  backup="${BACKUP:-}"
fi
if [[ -z "$backup" || ! -f "$backup" ]]; then
  latest="$(ls -t /tmp/thesisos-pre-demo-*.sql 2>/dev/null | head -1 || true)"
  backup="${latest:-}"
fi
if [[ -n "$backup" && -f "$backup" ]]; then
  size_bytes="$(stat -c '%s' "$backup" 2>/dev/null || echo 0)"
  if [[ "$size_bytes" -gt 1048576 ]]; then
    ok "backup exists ($(du -h "$backup" | cut -f1)) — $backup"
  else
    bad "backup too small ($size_bytes bytes): $backup"
  fi
else
  bad "no backup found — run: make demo-backup"
fi

echo "--- Corpus health (Docling defer) ---"
if ! curl -sf "$API/health" >/dev/null 2>&1; then
  bad "API not reachable at $API — run: make up"
  echo "demo-wave3-check: FAIL" >&2
  exit 1
fi

failed="$(docker compose exec -T db psql -U thesisos -d thesisos -At -c \
  "SELECT COUNT(*) FROM documents WHERE project_id='${PROJECT}' AND status='failed';" 2>/dev/null || echo 1)"
indexed="$(docker compose exec -T db psql -U thesisos -d thesisos -At -c \
  "SELECT COUNT(*) FROM documents WHERE project_id='${PROJECT}' AND status='indexed';" 2>/dev/null || echo 0)"

if [[ "${failed:-1}" -eq 0 ]]; then
  ok "0 failed documents (Docling defer OK for markdown demo)"
else
  bad "${failed} failed document(s) — fix or remove before demo"
fi

if [[ "${indexed:-0}" -ge 15 ]]; then
  ok "indexed documents = ${indexed} (>= 15)"
else
  bad "indexed documents = ${indexed} (expected >= 15)"
fi

echo "--- Mid-demo smoke ---"
# RAG retrieval smoke (not just ping)
rag_code="$(curl -s -o /tmp/demo_wave3_rag.json -w '%{http_code}' -X POST "$API/chat" \
  -H 'Content-Type: application/json' \
  -d "{\"message\":\"Cos'è STIGMATA nel corpus? Una frase.\",\"project_id\":\"${PROJECT}\"}" || echo 000)"
if [[ "$rag_code" == "200" ]]; then
  ok "POST /chat RAG smoke → 200"
else
  bad "POST /chat RAG smoke → $rag_code"
fi

# Showcase chapter opens
ch_code="$(curl -s -o /dev/null -w '%{http_code}' \
  "${API}/chapters/${SHOWCASE_ID}?project_id=${PROJECT}")"
if [[ "$ch_code" == "200" ]]; then
  ok "GET Cap. 3 vetrina → 200"
else
  bad "GET Cap. 3 vetrina → $ch_code"
fi

# Frontend surfaces (lightweight — no Playwright)
for path in / /writing /sources /settings; do
  fe_code="$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:3000${path}" || echo 000)"
  if [[ "$fe_code" == "200" ]]; then
    ok "frontend ${path} → 200"
  else
    bad "frontend ${path} → $fe_code"
  fi
done

echo "--- Tunnel (optional) ---"
if [[ -f /tmp/thesisos-beta-public.env ]]; then
  pub_url="$(rg '^PUBLIC_URL=' /tmp/thesisos-beta-public.env | cut -d= -f2- || true)"
  if [[ -n "$pub_url" ]] && curl -sf "${pub_url}/health" >/dev/null 2>&1; then
    ok "public tunnel health OK ($pub_url)"
  else
    bad "tunnel state exists but health failed — run: bash bin/beta-public-open.sh"
  fi
else
  ok "no public tunnel (localhost demo OK)"
fi

echo
if [[ "$fail" -eq 0 ]]; then
  echo "demo-wave3-check: PASS"
else
  echo "demo-wave3-check: FAIL" >&2
fi
exit "$fail"
