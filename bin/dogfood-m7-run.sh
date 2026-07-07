#!/usr/bin/env bash
# M7 product dogfood — full workflow gate script.
#
# Import → Index → Sources → Knowledge → Chat persist → Writing → Review → Export
#
# Requires a running stack (make up) and Vertex ADC for embedding/chat.
#
# Usage:
#   bin/dogfood-m7-run.sh [evidence.jsonl]
#   make dogfood-m7
set -euo pipefail

API="${API_BASE:-http://localhost:8000}"
PROJECT="${PROJECT_ID:-thesis-agent}"
OUT="${1:-/tmp/dogfood-m7-evidence.jsonl}"

log() { echo "$1" >> "$OUT"; }
fail() { echo "DOGFOOD M7 FAIL: $*" >&2; exit 1; }

jget() { python3 -c "import sys,json; print(json.load(sys.stdin)$1)"; }

parse_sse() {
  local raw="$1" expr="$2"
  printf '%s' "$raw" | python3 -c "
import sys, json
raw = sys.stdin.read().replace('\r\n', '\n')
parsed = {'conversation_id': None, 'sources_count': 0, 'tokens': []}
for block in raw.split('\n\n'):
    lines = [l for l in block.strip().split('\n') if l]
    if len(lines) < 2:
        continue
    ev = lines[0].split(':', 1)[1].strip()
    data = json.loads(lines[1][6:])
    if ev == 'done':
        parsed['conversation_id'] = data.get('conversation_id')
    elif ev == 'sources':
        parsed['sources_count'] = len(data.get('sources', []))
    elif ev == 'token':
        parsed['tokens'].append(data.get('text', ''))
parsed['answer'] = ''.join(parsed['tokens'])
$expr
"
}

curl -fsS --max-time 5 "$API/health" >/dev/null || fail "backend not reachable at $API (run: make up)"
: > "$OUT"
log "{\"step\":\"start\",\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"api\":\"$API\",\"project\":\"$PROJECT\"}"

# 1. Upload + index
MD=$(mktemp --suffix=.md); trap 'rm -f "$MD"' EXIT
cat > "$MD" <<'EOF'
# Dogfood M7 — workflow excerpt
Craftsmanship is the disciplined pursuit of quality in making.
This document validates the M7 import → index → retrieval path.
EOF
UPLOAD=$(curl -s -X POST "$API/upload" -F "file=@$MD;filename=dogfood_m7.md" -F "title=Dogfood M7 excerpt")
DOC_ID=$(echo "$UPLOAD" | jget "['id']")
for _ in $(seq 1 40); do
  STATUS=$(curl -s "$API/documents/$DOC_ID" | jget ".get('status','')")
  [[ "$STATUS" == "indexed" ]] && break
  [[ "$STATUS" == "failed" ]] && fail "indexing failed"
  sleep 2
done
[[ "$STATUS" == "indexed" ]] || fail "document did not reach indexed within timeout"
log "{\"step\":\"upload_index\",\"doc_id\":\"$DOC_ID\"}"

# 2. Search (corpus retrieval)
SEARCH=$(curl -s -X POST "$API/search" -H 'Content-Type: application/json' \
  -d "{\"query\":\"What is craftsmanship?\",\"limit\":5,\"document_ids\":[\"$DOC_ID\"]}")
echo "$SEARCH" | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d.get('results'), 'search returned no results'
" || fail "search did not return results"
log "{\"step\":\"search\",\"hits\":$(echo "$SEARCH" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('results',[])))")}"

# 3. Sources (DB-backed)
SOURCES=$(curl -s "$API/projects/$PROJECT/sources")
echo "$SOURCES" | python3 -c "
import sys, json
body = json.load(sys.stdin)
sources = body.get('sources', [])
assert sources, 'no sources from DB'
assert any(s.get('id') == 'benjamin-opera-arte' for s in sources), 'seed source missing'
" || fail "sources list not DB-backed"
log "{\"step\":\"sources\",\"count\":$(echo "$SOURCES" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('sources',[])))")}"

# 4. Knowledge (DB-backed)
KNOW=$(curl -s "$API/projects/$PROJECT/knowledge/objects")
echo "$KNOW" | python3 -c "
import sys, json
objs = json.load(sys.stdin).get('objects', [])
assert objs, 'knowledge objects empty'
" || fail "knowledge list empty"
KN_SEARCH=$(curl -s "$API/projects/$PROJECT/knowledge/search?q=aura")
echo "$KN_SEARCH" | python3 -c "
import sys, json
results = json.load(sys.stdin).get('results', [])
assert results, 'knowledge search returned nothing'
" || fail "knowledge search failed"
log "{\"step\":\"knowledge\",\"objects\":$(echo "$KNOW" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('objects',[])))")}"

# 5. Chat persistence
CONV=$(curl -s -X POST "$API/conversations" -H 'Content-Type: application/json' \
  -d "{\"project_id\":\"$PROJECT\",\"title\":\"M7 dogfood\"}")
CONV_ID=$(echo "$CONV" | jget "['id']")
CHAT=$(curl -sN -X POST "$API/chat" -H 'Content-Type: application/json' \
  -d "{\"conversation_id\":\"$CONV_ID\",\"project_id\":\"$PROJECT\",\"message\":\"Briefly summarize craftsmanship from my uploaded document. Cite sources.\"}")
parse_sse "$CHAT" "
assert parsed.get('conversation_id') == '$CONV_ID', 'conversation_id mismatch'
assert parsed.get('answer'), 'empty chat answer'
" >/dev/null || fail "chat turn failed"
MSGS=$(curl -s "$API/conversations/$CONV_ID/messages")
echo "$MSGS" | python3 -c "
import sys, json
items = json.load(sys.stdin).get('items', [])
assert len(items) >= 2, f'expected persisted messages, got {len(items)}'
" || fail "chat messages not persisted"
log "{\"step\":\"chat_persist\",\"conversation_id\":\"$CONV_ID\",\"messages\":$(echo "$MSGS" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('items',[])))")}"

# 6. Writing — chapter create + save
CH=$(curl -s -X POST "$API/chapters" -H 'Content-Type: application/json' \
  -d '{"title":"M7 dogfood chapter","content_md":"# Draft\n\nInitial paragraph."}')
CH_ID=$(echo "$CH" | jget "['id']")
VER=$(echo "$CH" | jget "['version']")
PATCHED=$(curl -s -X PATCH "$API/chapters/$CH_ID" -H 'Content-Type: application/json' \
  -d "{\"content_md\":\"# Draft\\n\\nRevised paragraph for M7.\",\"expected_version\":$VER}")
echo "$PATCHED" | python3 -c "
import sys, json
ch = json.load(sys.stdin)
assert ch.get('version') == 2, 'chapter version not incremented'
assert 'Revised paragraph' in (ch.get('content_md') or ''), 'content not saved'
" || fail "chapter save failed"
log "{\"step\":\"writing\",\"chapter_id\":\"$CH_ID\"}"

# 7. Review — proposal create + accept
PROP=$(curl -s -X POST "$API/proposals" -H 'Content-Type: application/json' \
  -d "{\"project_id\":\"$PROJECT\",\"chapter_id\":\"$CH_ID\",\"original\":\"Revised paragraph for M7.\",\"proposed\":\"Accepted paragraph for M7.\",\"action\":\"rewrite\"}")
PROP_ID=$(echo "$PROP" | jget "['id']")
ACCEPT=$(curl -s -X POST "$API/proposals/$PROP_ID/accept" -H 'Content-Type: application/json' \
  -d '{"expected_chapter_version":2}')
echo "$ACCEPT" | python3 -c "
import sys, json
body = json.load(sys.stdin)
assert body['chapter']['content_md'] == 'Accepted paragraph for M7.', 'accept did not apply'
assert body['chapter']['version'] == 3, 'chapter version not incremented after accept'
" || fail "proposal accept failed"
log "{\"step\":\"review\",\"proposal_id\":\"$PROP_ID\"}"

# 8. BibTeX export (DB)
BIB=$(curl -s "$API/projects/$PROJECT/sources/bibliography/export")
echo "$BIB" | python3 -c "
import sys
text = sys.stdin.read()
assert '@book{' in text, 'bibtex missing entries'
assert 'Benjamin' in text, 'approved Benjamin missing'
assert 'Barthes' not in text, 'excluded Barthes leaked'
" || fail "bibliography export failed"
log "{\"step\":\"bibtex_export\",\"bytes\":${#BIB}}"

# 9. Chapter markdown export
EXPORT=$(curl -s "$API/export/chapters/$CH_ID.md")
echo "$EXPORT" | python3 -c "
import sys
text = sys.stdin.read()
assert 'Accepted paragraph for M7.' in text, 'exported chapter missing accepted content'
" || fail "chapter markdown export failed"
log "{\"step\":\"chapter_export\",\"bytes\":${#EXPORT}}"

log "{\"step\":\"complete\",\"verdict\":\"pass\"}"
echo "DOGFOOD M7 PASS — evidence: $OUT"
