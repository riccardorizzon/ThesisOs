#!/usr/bin/env bash
# Wave 2 demo gate — verify polish applied (titles, export, sources, idempotent scripts).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

API="${THESISOS_API:-http://localhost:8000}"
PROJECT="${THESISOS_PROJECT_ID:-thesis-agent}"
SHOWCASE_ID="503c33f5-a3d8-40ee-adc0-3ff067747a17"
fail=0

ok() { echo "  OK  $*"; }
bad() { echo "  FAIL $*" >&2; fail=1; }

echo "=== demo-wave2-check (project=$PROJECT) ==="

if ! curl -sf "$API/health" >/dev/null 2>&1; then
  bad "API not reachable at $API — run: make up"
  exit 1
fi

echo "--- Chapter titles ---"
stats="$(docker compose exec -T db psql -U thesisos -d thesisos -At <<SQL
SELECT
  (SELECT COUNT(*) FROM chapters WHERE project_id='${PROJECT}' AND title ILIKE '[kimi-claw%'),
  (SELECT COUNT(*) FROM (SELECT title FROM chapters WHERE project_id='${PROJECT}' GROUP BY title HAVING COUNT(*)>1) d),
  (SELECT COUNT(*) FROM chapters WHERE project_id='${PROJECT}'),
  COALESCE((SELECT word_count FROM chapters WHERE id='${SHOWCASE_ID}'), 0);
SQL
)"
IFS='|' read -r kimi_titles dup_titles chapter_count showcase_wc <<<"$stats"

if [[ "${kimi_titles:-1}" -eq 0 ]]; then
  ok "no [kimi-claw-…] prefixes (${chapter_count} chapters)"
else
  bad "${kimi_titles} chapter(s) still have [kimi-claw-…] prefix"
fi

if [[ "${dup_titles:-1}" -eq 0 ]]; then
  ok "no duplicate chapter titles"
else
  bad "${dup_titles} duplicate chapter title group(s)"
fi

if [[ "${chapter_count:-0}" -eq 14 ]]; then
  ok "chapter count = 14"
else
  bad "chapter count = ${chapter_count} (expected 14)"
fi

if [[ "${showcase_wc:-0}" -ge 3000 ]]; then
  ok "showcase Cap. 3 word_count = ${showcase_wc}"
else
  bad "showcase Cap. 3 word_count = ${showcase_wc} (expected >= 3000)"
fi

echo "--- Export smoke ---"
ex_code="$(curl -s -o /dev/null -w '%{http_code}' \
  "${API}/export/chapters/${SHOWCASE_ID}.md?project_id=${PROJECT}")"
if [[ "$ex_code" == "200" ]]; then
  ok "export Cap. 3 markdown → 200"
else
  bad "export Cap. 3 markdown → $ex_code (expected 200)"
fi

no_proj_code="$(curl -s -o /dev/null -w '%{http_code}' \
  "${API}/export/chapters/${SHOWCASE_ID}.md")"
if [[ "$no_proj_code" == "422" ]]; then
  ok "export without project_id → 422"
else
  bad "export without project_id → $no_proj_code (expected 422)"
fi

echo "--- Sources ---"
linked="$(docker compose exec -T db psql -U thesisos -d thesisos -At -c \
  "SELECT COUNT(*) FROM sources WHERE project_id='${PROJECT}' AND document_id IS NOT NULL;" 2>/dev/null || echo 0)"
total="$(docker compose exec -T db psql -U thesisos -d thesisos -At -c \
  "SELECT COUNT(*) FROM sources WHERE project_id='${PROJECT}';" 2>/dev/null || echo 0)"
if [[ "$linked" == "$total" && "$total" == "11" ]]; then
  ok "sources linked ${linked}/${total}"
else
  bad "sources linked ${linked}/${total} (expected 11/11)"
fi

echo "--- Idempotent scripts ---"
wave2_out="$(bash bin/demo-wave2.sh --dry-run 2>&1 || true)"
if printf '%s\n' "$wave2_out" | rg -q '\(none pending\)'; then
  ok "demo-wave2.sh dry-run → nothing pending"
else
  bad "demo-wave2.sh dry-run reports pending actions"
fi

cleanup_out="$(bash bin/demo-cleanup.sh --dry-run 2>&1 || true)"
if printf '%s\n' "$cleanup_out" | rg -q 'none pending'; then
  ok "demo-cleanup.sh dry-run → nothing pending"
else
  bad "demo-cleanup.sh dry-run reports pending actions"
fi

echo
if [[ "$fail" -eq 0 ]]; then
  echo "demo-wave2-check: PASS"
else
  echo "demo-wave2-check: FAIL" >&2
fi
exit "$fail"
