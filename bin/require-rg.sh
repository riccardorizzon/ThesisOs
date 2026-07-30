#!/usr/bin/env bash
# Fail-closed ripgrep presence check for bin/ guards and make targets.
# Source:  . "$(dirname "$0")/require-rg.sh"
# Or run:  bash bin/require-rg.sh
set -euo pipefail

if ! command -v rg >/dev/null 2>&1; then
  echo "ERROR: ripgrep (rg) is required but not on PATH." >&2
  echo "Install: https://github.com/BurntSushi/ripgrep#installation" >&2
  echo "Without rg, scope/isolation/AP/ops guards pass vacuously." >&2
  exit 1
fi
