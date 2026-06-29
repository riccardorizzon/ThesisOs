#!/usr/bin/env bash
# M6 Writing Workspace dogfood — exercises the writer route + chapter persistence.
#
# 1. Upload a source doc and index it.
# 2. Ask the runtime to DRAFT a chapter grounded in the document (writer route);
#    assert a non-empty draft streams back. Records B_write.
# 3. Save the draft through the workspace surface: POST /chapters → PATCH content
#    (optimistic version) → re-read → assert versioned change stream (WRITE,EDIT).
#
# Requires a running stack (make up) and Vertex ADC for embedding/chat.
#
# Usage:
#   bin/dogfood-m6-writing-run.sh [evidence.jsonl]
#   make dogfood-m6
set -euo pipefail

API="${API_BASE:-http://localhost:8000}"
OUT="${1:-/tmp/dogfood-m6-evidence.jsonl}"

log() { echo "$1" >> "$OUT"; }
fail() { echo "DOGFOOD M6 FAIL: $*" >&2; exit 1; }

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

jget() { python3 -c "import sys,json; print(json.load(sys.stdin)$1)"; }

curl -fsS --max-time 5 "$API/health" >/dev/null || fail "backend not reachable at $API (run: make up)"
: > "$OUT"
log "{\"step\":\"start\",\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"api\":\"$API\"}"

# 1. Upload + index a grounding source.
MD=$(mktemp --suffix=.md); trap 'rm -f "$MD"' EXIT
cat > "$MD" <<'EOF'
# Dogfood M6 — craftsmanship excerpt
Craftsmanship is the disciplined pursuit of quality: the maker takes responsibility
for the whole result, iterating until the work is coherent and durable.
EOF
UPLOAD=$(curl -s -X POST "$API/upload" -F "file=@$MD;filename=dogfood_m6.md" -F "title=Dogfood M6 excerpt")
DOC_ID=$(echo "$UPLOAD" | jget "['id']")
for _ in $(seq 1 40); do
  STATUS=$(curl -s "$API/documents/$DOC_ID" | jget ".get('status','')")
  [[ "$STATUS" == "indexed" ]] && break
  [[ "$STATUS" == "failed" ]] && fail "indexing failed"
  sleep 2
done

# 2. Writer turn — draft a chapter grounded in the document.
T0=$(date +%s.%N)
CHAT=$(curl -sN -X POST "$API/chat" -H 'Content-Type: application/json' \
  -d '{"message":"Write the chapter on craftsmanship, grounded in my uploaded document. Cite sources."}')
B_WRITE=$(echo "$(date +%s.%N) - $T0" | bc)
DRAFT=$(parse_sse "$CHAT" "
assert parsed.get('answer'), 'empty draft'
print(parsed['answer'])
") || fail "writer turn produced no draft"
log "{\"step\":\"writer\",\"b_write_s\":$B_WRITE,\"draft_chars\":${#DRAFT}}"

# 3. Save the draft through the workspace surface (POST → PATCH → re-read → history).
CH=$(curl -s -X POST "$API/chapters" -H 'Content-Type: application/json' \
  -d '{"title":"Craftsmanship (dogfood M6)"}')
CH_ID=$(echo "$CH" | jget "['id']")
VER=$(echo "$CH" | jget "['version']")
PATCHED=$(curl -s -X PATCH "$API/chapters/$CH_ID" -H 'Content-Type: application/json' \
  -d "$(DRAFT="$DRAFT" VER="$VER" python3 -c "import os,json; print(json.dumps({'content_md': os.environ['DRAFT'], 'expected_version': int(os.environ['VER'])}))")")
echo "$PATCHED" | python3 -c "
import sys, json
ch = json.load(sys.stdin)
assert ch.get('version') == 2, f'expected version 2, got {ch.get(\"version\")}'
assert ch.get('content_md'), 'chapter content not saved'
print('saved')
" >/dev/null || fail "chapter save did not version content"

VERSIONS=$(curl -s "$API/chapters/$CH_ID/versions" | python3 -c "
import sys, json
vs = json.load(sys.stdin)
kinds = [v['change_kind'] for v in vs]
assert kinds == ['WRITE', 'EDIT'], f'unexpected change stream: {kinds}'
print(len(vs))
") || fail "chapter change stream incorrect"
log "{\"step\":\"chapter_save\",\"chapter_id\":\"$CH_ID\",\"versions\":$VERSIONS}"

log "{\"step\":\"complete\",\"verdict\":\"pass\"}"
echo "DOGFOOD M6 PASS — evidence: $OUT (B_write=${B_WRITE}s)"
