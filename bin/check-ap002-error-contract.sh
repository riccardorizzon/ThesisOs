#!/usr/bin/env bash
# AP-002 — Error Contract: forbid silent SSR empty fallback after API load (Theme B).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=require-rg.sh
. "$ROOT/bin/require-rg.sh"

APP_DIR="${ROOT}/frontend/app"
FAIL=0

while IFS= read -r -d '' page; do
  rel="${page#"$ROOT"/}"
  if rg -q 'await\s+(chapterClient|listKnowledge|listSources|getSource|loadContext|proposalClient|conversationClient|projectsClient|documentClient|memoryClient|getKnowledge|getJobFsm)' "$page" 2>/dev/null; then
    if rg -U 'catch\s*\{[^}]*return\s+(\[\]|0|null)\s*;?' "$page" >/dev/null 2>&1; then
      echo "AP-002 FAIL: silent empty SSR fallback in $rel"
      rg -n 'catch' "$page" || true
      FAIL=1
    fi
  fi
done < <(find "$APP_DIR" -name 'page.tsx' -print0)

if [[ "$FAIL" -ne 0 ]]; then
  echo "Use Error Contract v1 — Error Surface or Degraded State (docs/engineering/error-contract-v1.md)."
  exit 1
fi

echo "AP-002 PASS: no silent SSR empty fallback on API loaders in app/**/page.tsx"
