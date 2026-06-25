#!/usr/bin/env bash
# Builder Memory preflight — run before orchestrate-builders wave dispatch.
# Warns if index is stale; optionally refreshes incrementally.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
CLI="${ROOT}/builder_memory/.venv/bin/builder-memory"

if [[ ! -x "$CLI" ]]; then
  echo "WARN: builder-memory CLI not installed. Run: cd builder_memory && python3 -m venv .venv && .venv/bin/pip install -e ."
  exit 0
fi

"$CLI" index --incremental --repo-root "$ROOT"

MANIFEST="${ROOT}/.builder-memory/manifest.json"
HEAD="$(git -C "$ROOT" rev-parse HEAD)"
INDEX_SHA="$(python3 -c "import json; print(json.load(open('${MANIFEST}'))['commit_sha'])" 2>/dev/null || echo "")"

if [[ "$INDEX_SHA" != "$HEAD" ]]; then
  echo "WARN: Builder Memory index may be stale (index=${INDEX_SHA:0:8} HEAD=${HEAD:0:8})"
else
  echo "OK: Builder Memory index fresh @ ${HEAD:0:8}"
fi
