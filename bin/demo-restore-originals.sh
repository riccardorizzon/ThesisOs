#!/usr/bin/env bash
# Restore missing on-disk originals for thesis-agent documents from knowledge/.
# Does NOT re-parse or re-embed — only restores downloadable files in document_data.
# Usage: bash bin/demo-restore-originals.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
KNOW="$ROOT/knowledge/thesis-agent"

# document_id|relative_path_under_knowledge|original_filename
MAP=(
  "0151175a-2a61-4095-b9c5-a86152151ed0|04_KNOWLEDGE/Books/Albers_Interaction-of-Color.md|Albers_Interaction-of-Color.md"
  "aa23bef3-32f4-4723-acf0-7cf3cc09ee93|04_KNOWLEDGE/Books/Barthes_Mythologies.md|Barthes_Mythologies.md"
  "fcb97bcc-e3e4-4e34-92c7-a29f50159b77|04_KNOWLEDGE/Books/Csikszentmihalyi_Flow.md|Csikszentmihalyi_Flow.md"
  "9e7eec1a-1187-48d4-8544-2b5980e62d1e|04_KNOWLEDGE/Books/Hollander_Sex-and-Suits.md|Hollander_Sex-and-Suits.md"
  "1b3d08ec-fa6d-494b-a034-8aef8ac0e98f|04_KNOWLEDGE/Books/Lobach_Disegno-Industriale.md|Lobach_Disegno-Industriale.md"
  "1834a737-bf25-4cae-a400-b6bede6c8700|04_KNOWLEDGE/Books/Seivewright_Basics-Fashion-Research.md|Seivewright_Basics-Fashion-Research.md"
  "92bc3231-2729-4e41-8dd4-826179d8d38b|04_KNOWLEDGE/Bibliography/Tesi-bibliografia-completa.md|Tesi-bibliografia-completa.md"
  "95f2e49a-1384-4457-b57f-7e9348e23161|03_PROJECT/Bibliography-Master.md|Bibliography-Master.md"
  "13788fcb-385f-409c-b2aa-d53236932a5e|04_KNOWLEDGE/Relatrice/prima-revisione-2026-05-27.pdf|prima-revisione-2026-05-27.pdf"
)

echo "=== demo-restore-originals ==="
if ! docker compose ps backend 2>/dev/null | rg -q 'Up'; then
  echo "FAIL: backend not Up" >&2
  exit 1
fi

ok=0
fail=0
for row in "${MAP[@]}"; do
  IFS='|' read -r doc_id rel fname <<<"$row"
  src="$KNOW/$rel"
  dest="/data/documents/documents/${doc_id}/original/${fname}"
  if [[ ! -f "$src" ]]; then
    echo "  FAIL missing source: $rel"
    fail=$((fail + 1))
    continue
  fi
  docker compose exec -T backend mkdir -p "/data/documents/documents/${doc_id}/original"
  docker compose cp "$src" "backend:${dest}" >/dev/null
  if docker compose exec -T backend test -f "$dest"; then
    size="$(docker compose exec -T backend stat -c '%s' "$dest" 2>/dev/null || echo '?')"
    echo "  OK  ${fname} → ${doc_id:0:8}… (${size} bytes)"
    ok=$((ok + 1))
  else
    echo "  FAIL copy ${fname}"
    fail=$((fail + 1))
  fi
done

echo
echo "Restored: $ok  Failed: $fail"
bash bin/audit-document-storage.sh 2>&1 | head -20
[[ "$fail" -eq 0 ]]
