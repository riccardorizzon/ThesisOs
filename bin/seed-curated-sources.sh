#!/usr/bin/env bash
# Upload curated thesis markdown from knowledge/thesis-agent into Sources + index.
# Restores on-disk originals for core corpus files (P1 curated, not bulk dogfood).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

API="${THESISOS_API:-http://localhost:8000}"
KNOW="${ROOT}/knowledge/thesis-agent"
PROJECT="${THESISOS_PROJECT_ID:-thesis-agent}"

# Core thesis SoR files — paths relative to knowledge/thesis-agent
FILES=(
  "03_PROJECT/Outline-Master.md"
  "03_PROJECT/Stigmata-Framework.md"
  "03_PROJECT/Core-Theory-Map.md"
  "04_KNOWLEDGE/Books/Sennett_The-Craftsman.md"
  "04_KNOWLEDGE/Books/Benjamin_Opera-Arte-Riproducibilita.md"
  "04_KNOWLEDGE/University/Guida-Redazione-Tesi.md"
)

if ! curl -sf "$API/health" >/dev/null; then
  echo "API not reachable at $API — start stack: make up"
  exit 1
fi

upload_one() {
  local rel="$1"
  local path="$KNOW/$rel"
  local base title
  base="$(basename "$path")"
  title="${base%.md}"

  if [[ ! -f "$path" ]]; then
    echo "SKIP missing: $rel"
    return 0
  fi

  echo "UPLOAD $rel ..."
  local resp
  resp="$(curl -s -w '\n%{http_code}' -X POST "$API/upload" \
    -F "file=@${path};filename=${base};type=text/markdown" \
    -F "title=${title}" \
    -F "project_id=${PROJECT}" \
    -F "language=it")"
  local code body id
  code="$(echo "$resp" | tail -1)"
  body="$(echo "$resp" | sed '$d')"
  if [[ "$code" != "201" ]]; then
    echo "  FAIL HTTP $code: $body"
    return 1
  fi
  id="$(echo "$body" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null || true)"
  if [[ -z "$id" ]]; then
    echo "  OK uploaded (no id parsed)"
    return 0
  fi
  echo "  id=$id — waiting for indexed ..."
  for _ in $(seq 1 60); do
    sleep 2
    st="$(curl -s "$API/documents/${id}?project_id=${PROJECT}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null || echo "")"
    case "$st" in
      indexed) echo "  indexed"; return 0 ;;
      failed)
        err="$(curl -s "$API/documents/${id}?project_id=${PROJECT}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('error_message',''))" 2>/dev/null || echo "")"
        echo "  FAIL status=failed: $err"
        return 1
        ;;
      parsed) ;; # still embedding
      *) ;;
    esac
  done
  echo "  WARN timeout waiting for indexed (last status=$st)"
  return 0
}

echo "=== Seed curated thesis sources → $API (project=$PROJECT) ==="
failed=0
for f in "${FILES[@]}"; do
  upload_one "$f" || failed=$((failed + 1))
done

echo
echo "=== Post-seed audit ==="
bash "$ROOT/bin/audit-document-storage.sh" | rg 'Documents in DB|Original on disk|Missing originals' || true

if [[ "$failed" -gt 0 ]]; then
  echo "seed-curated-sources: $failed upload(s) failed"
  exit 1
fi
echo "seed-curated-sources: done"
