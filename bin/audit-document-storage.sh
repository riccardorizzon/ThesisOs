#!/usr/bin/env bash
# Audit Postgres documents vs on-disk originals (local storage adapter).
# Reports rows whose original bytes are missing — common after pre-volume /tmp era.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DB_URL="${DATABASE_URL:-postgresql+psycopg://thesisos:thesisos@localhost:5432/thesisos}"

echo "=== ThesisOS document storage audit ==="
echo "DB: ${DB_URL%%@*}@***"
echo

# Prefer running inside backend container for path alignment
if docker compose ps backend 2>/dev/null | rg -q 'Up'; then
  BASE_DIR="$(docker compose exec -T backend printenv DOCUMENT_STORAGE_LOCAL_DIR 2>/dev/null || echo /data/documents)"
  echo "Storage base (container): $BASE_DIR"
  echo

  docker compose exec -T backend python - <<'PY'
import os
import re
from pathlib import Path

import psycopg

SAFE = re.compile(r"[^A-Za-z0-9._-]")

def sanitize(name: str | None) -> str:
    base = (name or "file").replace("\\", "/").split("/")[-1]
    cleaned = SAFE.sub("_", base).strip("_")
    return cleaned or "file"

def key(doc_id: str, filename: str | None) -> str:
    return f"documents/{doc_id}/original/{sanitize(filename)}"

db_url = os.environ.get("DATABASE_URL", "postgresql+psycopg://thesisos:thesisos@db:5432/thesisos")
base = Path(os.environ.get("DOCUMENT_STORAGE_LOCAL_DIR", "/data/documents"))

with psycopg.connect(db_url.replace("+psycopg", "")) as conn:
    rows = conn.execute(
        """
        SELECT d.id::text, d.original_filename, d.title, d.status,
               (SELECT COUNT(*) FROM chunks c WHERE c.document_id = d.id) AS chunk_count
        FROM documents d
        ORDER BY d.created_at
        """
    ).fetchall()

missing = []
present = []
for doc_id, orig, title, status, chunks in rows:
    path = base / key(doc_id, orig)
    if path.is_file():
        present.append((doc_id, title, status, chunks, path))
    else:
        missing.append((doc_id, title, status, chunks, path))

print(f"Documents in DB:     {len(rows)}")
print(f"Original on disk:    {len(present)}")
print(f"Missing originals:   {len(missing)}")
print()

if missing:
    print("--- Missing originals (RAG may still work if chunks/embeddings exist) ---")
    for doc_id, title, status, chunks, path in missing[:20]:
        print(f"  {doc_id[:8]}…  status={status:10} chunks={chunks:4}  {title[:50]}")
    if len(missing) > 20:
        print(f"  … and {len(missing) - 20} more")
    print()
    print("Recovery: re-upload via /sources/upload if you need re-parse or download.")
    print("          Indexed chunks in Postgres are unaffected until re-parse.")

if present:
    print("--- Sample present ---")
    for doc_id, title, status, chunks, path in present[:5]:
        print(f"  {doc_id[:8]}…  {path}")

failed = [r for r in rows if r[3] == "failed"]
if failed:
    print()
    print(f"--- Failed parse ({len(failed)}) — check error_message, not storage ---")
    with psycopg.connect(db_url.replace("+psycopg", "")) as conn:
        for row in conn.execute(
            "SELECT title, error_message FROM documents WHERE status='failed'"
        ):
            print(f"  {row[0][:50]}: {row[1]}")
PY
else
  echo "Backend container not running — start with: docker compose up -d backend"
  exit 1
fi

echo
echo "=== Volume ==="
docker volume ls | rg document_data || echo "(no document_data volume)"
