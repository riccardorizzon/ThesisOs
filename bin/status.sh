#!/usr/bin/env bash
# ThesisOS Developer Cockpit (v0) — answers "where are we?" at a glance.
# Read-only. Combines LIVE signals (git tags, docker, /health, metadata server)
# with the canonical snapshot files we already maintain. No state of its own.
set -uo pipefail
cd "$(dirname "$0")/.." 2>/dev/null || exit 1

CS="knowledge/context/current-state.md"
NA="knowledge/context/next-actions.md"
STATE="plans/builder/STATE.yaml"
API="${API_BASE:-http://localhost:8000}"

# --- product -----------------------------------------------------------------
# Two views, two questions: how much project is built vs how much the user sees.
TOTAL_MILESTONES=18   # roadmap span M1–M18 (knowledge/project/roadmap.md)
done_total=$(git tag -l 'm[0-9]*-complete' 2>/dev/null | wc -l | tr -d ' ')
features=$(git tag -l 'm[1-9]*-complete' 2>/dev/null | wc -l | tr -d ' ')
if git tag -l 'm0-complete' 2>/dev/null | grep -q .; then foundations="M0 ✓"; else foundations="M0 ✗"; fi
priority=$(awk '/## What is next/{f=1;next} f&&/^[0-9]+\./{sub(/^[0-9]+\.[[:space:]]*/,"");gsub(/\*\*/,"");print;exit}' "$CS" 2>/dev/null)
[ -z "$priority" ] && priority="(see $CS)"

# --- ASEP --------------------------------------------------------------------
if grep -qi 'ASEP = maintenance' "$NA" 2>/dev/null; then asep="Maintenance"; else asep="(see $NA)"; fi
blocked=$(awk '/^blockers:/{print ($0 ~ /\{\}/)?"No":"YES (see STATE.yaml)";exit}' "$STATE" 2>/dev/null)
[ -z "$blocked" ] && blocked="?"

# --- infrastructure (live) ---------------------------------------------------
if curl -fsS --max-time 1 -H 'Metadata-Flavor: Google' \
   http://metadata.google.internal/computeMetadata/v1/instance/name >/dev/null 2>&1; then
  envlabel="GCP VM"; else envlabel="local"; fi
health=$(curl -fsS --max-time 2 "$API/health" >/dev/null 2>&1 && echo OK || echo down)
running=$(docker compose ps --services --status=running 2>/dev/null || true)
be=$(printf '%s\n' "$running" | grep -qx backend && echo Running || echo "—")
fe=$(printf '%s\n' "$running" | grep -qx frontend && echo Running || echo "—")
db=$(docker compose ps db 2>/dev/null | grep -qi healthy && echo Healthy || echo "—")
if [ -n "${GOOGLE_CLOUD_PROJECT:-}" ]; then vertex="configured (${GOOGLE_CLOUD_PROJECT})"; else vertex="stub — set GOOGLE_CLOUD_PROJECT"; fi

bar="════════════════════════════════════════════════"
printf '%s\n  THESISOS STATUS\n%s\n' "$bar" "$bar"
printf '\nPRODUCT\n  Foundations  : %s\n  User features : %s\n  Milestones   : %s / %s\n  Priority     : %s\n' \
  "$foundations" "$features" "$done_total" "$TOTAL_MILESTONES" "$priority"
printf '\nASEP\n  Mode       : %s\n  Blocked?   : %s\n' "$asep" "$blocked"
printf '\nINFRASTRUCTURE\n  Environment: %s\n  Backend    : %s  (/health %s)\n  Frontend   : %s\n  Database   : %s\n  Vertex     : %s\n' \
  "$envlabel" "$be" "$health" "$fe" "$db" "$vertex"
printf '%s\n' "$bar"
