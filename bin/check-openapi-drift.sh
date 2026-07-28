#!/usr/bin/env bash
# Fail when watched FastAPI routes are missing from contracts/openapi/openapi.yaml.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"

exec .venv/bin/python - <<'PY'
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

from app.main import app

ROOT = Path.cwd().parent
CONTRACT = ROOT / "contracts" / "openapi" / "openapi.yaml"


def watched(path: str) -> bool:
    return (
        path.startswith("/chapters")
        or path.startswith("/export")
        or path.startswith("/writing")
        or "/knowledge/" in path
        or "/companion/" in path
    )


def norm(path: str) -> str:
    return re.sub(r"\{[^}]+\}", "{}", path)


live = {norm(p) for p in app.openapi()["paths"] if watched(p)}
declared = {norm(p) for p in yaml.safe_load(CONTRACT.read_text())["paths"] if watched(p)}
missing = sorted(live - declared)

if missing:
    print("OpenAPI contract missing watched routes:", file=sys.stderr)
    for path in missing:
        print(f"  {path}", file=sys.stderr)
    sys.exit(1)

print("openapi-drift OK")
PY
