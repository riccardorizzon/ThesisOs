#!/usr/bin/env bash
# Pre-demo DB backup — writes timestamped dump and records latest path.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="${THESISOS_BACKUP:-/tmp/thesisos-pre-demo-${STAMP}.sql}"
STATE="/tmp/thesisos-latest-backup.env"

echo "=== demo-backup ==="
echo "Target: $OUT"

if ! docker compose ps db 2>/dev/null | rg -q 'Up'; then
  echo "FAIL: db container not Up (run: make up)" >&2
  exit 1
fi

docker compose exec -T db pg_dump -U thesisos thesisos > "$OUT"
size="$(du -h "$OUT" | cut -f1)"
echo "BACKUP=$OUT" | tee "$STATE"
echo "SIZE=$size" | tee -a "$STATE"
echo "CREATED=$(date -Iseconds)" | tee -a "$STATE"

echo "demo-backup: OK ($size)"
