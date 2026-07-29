#!/usr/bin/env bash
# Cohort materials gate — invite pack + tracker + operator checklist (no fake humans).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail=0
ok() { echo "  OK  $*"; }
bad() { echo "  FAIL $*" >&2; fail=1; }

echo "=== cohort-check ==="

INVITE=".asep/reports/BETA-COHORT-INVITE.md"
TRACKER=".asep/reports/THESISOS-v2.0.0-rc.2-BETA-VALIDATION.md"
ONBOARD=".asep/reports/RC-BETA-ONBOARDING.md"
HANDOUT="docs/demo/DEMO-HANDOUT.md"

for f in "$INVITE" "$TRACKER" "$ONBOARD" "$HANDOUT"; do
  if [[ -f "$f" ]]; then ok "$f present"; else bad "$f missing"; fi
done

echo "--- Invite pack content ---"
if rg -q 'Messaggio invito|copia-incolla' "$INVITE" 2>/dev/null; then
  ok "invite copy-paste block present"
else
  bad "invite message missing"
fi

if rg -q 'Checklist operatore|Operator checklist' "$INVITE" 2>/dev/null; then
  ok "operator checklist present"
else
  bad "operator checklist missing in BETA-COHORT-INVITE"
fi

if rg -q 'BETA_ACCESS_TOKEN|X-Beta-Token|ADR-0048' "$INVITE" 2>/dev/null; then
  ok "shared beta gate documented for cohort URL"
else
  bad "ADR-0048 / BETA_ACCESS_TOKEN not mentioned in invite pack"
fi

echo "--- Tracker slots ---"
if [[ -f "$TRACKER" ]]; then
  slots="$(rg -c '^\| [0-9]+ \|' "$TRACKER" 2>/dev/null || echo 0)"
  if [[ "${slots:-0}" -ge 10 ]]; then
    ok "cohort tracker has ${slots} slots (>= 10)"
  else
    bad "cohort tracker has ${slots} slots (expected >= 10)"
  fi
fi

echo "--- Honest beta limitations ---"
if rg -q 'Single-user|single-user' "$HANDOUT" 2>/dev/null; then
  ok "handout declares single-user"
else
  bad "handout missing single-user limitation"
fi

if rg -q 'W-06|author-date|Citazioni' "$HANDOUT" 2>/dev/null; then
  ok "handout documents citation residual (W-06)"
else
  bad "handout missing citation limitation"
fi

echo
if [[ "$fail" -eq 0 ]]; then
  echo "cohort-check: PASS"
else
  echo "cohort-check: FAIL" >&2
fi
exit "$fail"
