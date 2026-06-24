#!/usr/bin/env bash
# Clone curated UI/UX reference repos for ThesisOS (Next.js + Tailwind).
# Requires ~2–4 GB free disk space. Run from repo root:
#   bash scripts/download-ui-libraries.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${ROOT}/references/ui-libraries"

MIN_MB=2048
avail_kb="$(df -k "$ROOT" | awk 'NR==2 {print $4}')"
avail_mb=$((avail_kb / 1024))
if (( avail_mb < MIN_MB )); then
  echo "Need at least ${MIN_MB} MB free; only ${avail_mb} MB available."
  echo "Free space (e.g. clear ~/.cache, remove old builds) and retry."
  exit 1
fi

mkdir -p "$DEST"
cd "$DEST"

repos=(
  "shadcn-ui/ui"           # Base design system — Radix + Tailwind (copy-paste model)
  "pacifio/ui"             # Agent/chat/dashboard UI patterns (fits ThesisOS)
  "keenthemes/reui"        # 1000+ shadcn dashboard patterns
  "magicuidesign/magic-ui" # Polished marketing / hero animations
  "origin-space/originui"  # Clean professional components
  "tremorlabs/tremor"      # Dashboard charts + data viz
  "ibelick/ui"             # Minimal shadcn-style blocks
  "shadcnblockscom/shadcn-ui-blocks" # Full page layouts
)

for repo in "${repos[@]}"; do
  name="${repo//\//-}"
  if [[ -d "$name/.git" ]]; then
    echo "Skip (exists): $name"
    continue
  fi
  echo "Cloning $repo -> $name"
  git clone --depth 1 "https://github.com/${repo}.git" "$name"
done

echo ""
echo "Done. Libraries in: $DEST"
echo "Next: cd frontend && npx shadcn@latest init -y -d && npx shadcn@latest add button card sidebar dialog"
