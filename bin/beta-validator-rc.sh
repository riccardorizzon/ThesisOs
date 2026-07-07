#!/usr/bin/env bash
# RC beta validator — rerun staging checks for ThesisOS v2.0.0-rc.1.
# Operational only; no product mutations. Exit 0 = PASS.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
E2E="$ROOT/tests/e2e"
FRONTEND_URL="${BETA_FRONTEND_URL:-http://127.0.0.1:3000}"
API_URL="${BETA_API_URL:-http://127.0.0.1:8000}"
LOG="${BETA_VALIDATOR_LOG:-/tmp/beta-validator-rc.log}"

RC_SPEC="$(mktemp /tmp/rc-beta-validation.XXXXXX.spec.ts)"
trap 'rm -f "$RC_SPEC"' EXIT

cat >"$RC_SPEC" <<'EOF'
import { test, expect } from "@playwright/test";

const SURFACES = [
  { name: "Home", path: "/", check: async (p) => { await expect(p.getByRole("heading", { name: "Home", level: 1 })).toBeVisible(); }},
  { name: "Writing", path: "/writing", check: async (p) => { await expect(p.getByTestId("writing-workspace")).toBeVisible(); }},
  { name: "Knowledge", path: "/knowledge", check: async (p) => { await expect(p.getByRole("heading", { name: "Knowledge", level: 1 })).toBeVisible(); }},
  { name: "Sources", path: "/sources", check: async (p) => { await expect(p.getByRole("heading", { name: "Sources", level: 1 })).toBeVisible(); }},
  { name: "Research Canvas", path: "/research/canvas", check: async (p) => { await p.setViewportSize({ width: 1280, height: 800 }); await expect(p.getByTestId("research-canvas-shell")).toBeVisible(); }},
  { name: "Settings", path: "/settings", check: async (p) => { await expect(p.getByTestId("settings-page")).toBeVisible(); }},
];

test.describe("RC beta validation", () => {
  for (const s of SURFACES) {
    test(s.name, async ({ page }) => { await page.goto(s.path); await s.check(page); });
  }
});
EOF

echo "=== RC Beta Validator — $(date -Iseconds) ===" | tee "$LOG"
echo "frontend=$FRONTEND_URL api=$API_URL" | tee -a "$LOG"

fail=0

echo "--- health ---" | tee -a "$LOG"
curl -sf "$API_URL/health" | tee -a "$LOG" || fail=1
echo | tee -a "$LOG"

echo "--- HTTP routes ---" | tee -a "$LOG"
for path in / /writing /knowledge /sources /research/canvas /settings; do
  code=$(curl -sf -o /dev/null -w '%{http_code}' "$FRONTEND_URL$path" || echo fail)
  echo "$path -> $code" | tee -a "$LOG"
  [ "$code" = "200" ] || fail=1
done

echo "--- context API ---" | tee -a "$LOG"
curl -sf "$API_URL/projects/thesis-agent/context?surface=home" >/dev/null || fail=1
echo "context API OK" | tee -a "$LOG"

echo "--- playwright ---" | tee -a "$LOG"
cd "$E2E"
PLAYWRIGHT_SKIP_WEBSERVER=1 \
  PLAYWRIGHT_BASE_URL="$FRONTEND_URL" \
  E2E_API_BASE_URL="$API_URL" \
  npx playwright test "$RC_SPEC" px1-context-api.spec.ts 2>&1 | tee -a "$LOG" || fail=1

if [ "$fail" -eq 0 ]; then
  echo "VERDICT: PASS" | tee -a "$LOG"
  exit 0
fi
echo "VERDICT: FAIL" | tee -a "$LOG"
exit 1
