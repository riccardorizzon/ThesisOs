#!/usr/bin/env bash
# Create thesisos_test (if missing) and apply Alembic migrations.
# Used by backend pytest (conftest) and `make ci` so tests never touch the dev DB.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$ROOT/backend"

TEST_DATABASE_URL="${TEST_DATABASE_URL:-postgresql+psycopg://thesisos:thesisos@localhost:5432/thesisos_test}"
DB_NAME="${TEST_DATABASE_URL##*/}"

cd "$BACKEND"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  .venv/bin/pip install -q -e ".[dev]"
fi

# Create database when Postgres is reachable (docker compose db or local instance).
.venv/bin/python - "$TEST_DATABASE_URL" "$DB_NAME" <<'PY'
import sys
from urllib.parse import urlparse

import psycopg

test_url = sys.argv[1]
db_name = sys.argv[2]
parsed = urlparse(test_url.replace("+psycopg", ""))
admin_url = (
    f"postgresql://{parsed.username}:{parsed.password}"
    f"@{parsed.hostname}:{parsed.port or 5432}/postgres"
)

try:
    with psycopg.connect(admin_url, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            if cur.fetchone() is None:
                cur.execute(f'CREATE DATABASE "{db_name}"')
except Exception as exc:
    print(f"ensure-test-db: Postgres not reachable ({exc}); pytest will skip DB tests", file=sys.stderr)
    sys.exit(0)
PY

export DATABASE_URL="$TEST_DATABASE_URL"
.venv/bin/alembic upgrade head
