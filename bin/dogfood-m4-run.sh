#!/usr/bin/env bash
# M4 product dogfood runner — repeatable regression check for M4+ milestones.
#
# Exercises: upload → index → search → memory → grounded chat → follow-up.
# Requires a running stack (make up) and Vertex ADC for embedding/chat.
#
# Usage:
#   bin/dogfood-m4-run.sh [evidence.jsonl]
#   make dogfood-m4
#
# Exit 0 on success; non-zero on any failed assertion.
set -euo pipefail

API="${API_BASE:-http://localhost:8000}"
OUT="${1:-/tmp/dogfood-m4-evidence.jsonl}"
CRAFTSMAN_ID="${CRAFTSMAN_ID:-c31abf2c-a069-4919-b7fb-5eeb6cbebc19}"

log() { echo "$1" >> "$OUT"; }

fail() { echo "DOGFOOD FAIL: $*" >&2; exit 1; }

parse_sse() {
  # Usage: parse_sse <raw_sse> <python_expr_on_parsed_dict>
  local raw="$1" expr="$2"
  printf '%s' "$raw" | python3 -c "
import sys, json
raw = sys.stdin.read().replace('\r\n', '\n')
parsed = {'conversation_id': None, 'sources_count': 0, 'tokens': [], 'sources': []}
for block in raw.split('\n\n'):
    lines = [l for l in block.strip().split('\n') if l]
    if len(lines) < 2:
        continue
    ev = lines[0].split(':', 1)[1].strip()
    data = json.loads(lines[1][6:])
    if ev == 'done':
        parsed['conversation_id'] = data.get('conversation_id')
    elif ev == 'sources':
        parsed['sources'] = data.get('sources', [])
        parsed['sources_count'] = len(parsed['sources'])
    elif ev == 'token':
        parsed['tokens'].append(data.get('text', ''))
parsed['answer'] = ''.join(parsed['tokens'])
$expr
"
}

# --- preflight ---------------------------------------------------------------
curl -fsS --max-time 5 "$API/health" >/dev/null || fail "backend not reachable at $API (run: make up)"

: > "$OUT"
log "{\"step\":\"start\",\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"api\":\"$API\"}"

# 1. Upload
MD=$(mktemp --suffix=.md)
trap 'rm -f "$MD"' EXIT
cat > "$MD" <<'EOF'
# Dogfood M4 — Sennett excerpt

Richard Sennett argues that craftsmanship is **the desire to do a job well for its own sake**.
This passage is used to validate grounded retrieval after the M4 recovery sprint.
EOF

UPLOAD=$(curl -s -X POST "$API/upload" \
  -F "file=@$MD;filename=dogfood_m4.md" \
  -F "title=Dogfood M4 Sennett excerpt")
DOC_ID=$(echo "$UPLOAD" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
log "{\"step\":\"upload\",\"doc_id\":\"$DOC_ID\",\"response\":$UPLOAD}"

# 2. Index (poll)
INDEXED=false
for i in $(seq 1 40); do
  DOC=$(curl -s "$API/documents/$DOC_ID")
  STATUS=$(echo "$DOC" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))")
  if [[ "$STATUS" == "indexed" ]]; then
    INDEXED=true
    log "{\"step\":\"index\",\"attempt\":$i,\"response\":$DOC}"
    break
  fi
  if [[ "$STATUS" == "failed" ]]; then
    log "{\"step\":\"index\",\"attempt\":$i,\"response\":$DOC}"
    fail "document indexing failed (status=failed)"
  fi
  sleep 2
done
[[ "$INDEXED" == true ]] || fail "document did not reach indexed within timeout"

# 3. Retrieve
SEARCH=$(curl -s -X POST "$API/search" -H 'Content-Type: application/json' \
  -d "{\"query\":\"What is craftsmanship according to Sennett?\",\"limit\":5,\"document_ids\":[\"$DOC_ID\"]}")
log "{\"step\":\"search\",\"response\":$SEARCH}"
echo "$SEARCH" | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d.get('results'), 'search returned no results'
assert any(r.get('document_id') == '$DOC_ID' for r in d['results']), 'dogfood doc not in search results'
" || fail "search did not return dogfood document"

# 4. Memory
MEM=$(curl -s -X POST "$API/memory" -H 'Content-Type: application/json' \
  -d '{"kind":"thesis","content":"This thesis discusses Richard Sennett'\''s book The Craftsman and the ethics of skilled work.","pinned":true}')
log "{\"step\":\"memory\",\"response\":$MEM}"

# 5. Grounded chat (turn 1)
CHAT1=$(curl -sN -X POST "$API/chat" -H 'Content-Type: application/json' \
  -d '{"message":"According to my uploaded document, how does Sennett define craftsmanship? Cite sources."}')
PARSED1=$(parse_sse "$CHAT1" "
import json
assert parsed.get('conversation_id'), 'missing conversation_id'
assert parsed.get('sources_count', 0) > 0, 'missing sources event'
assert parsed.get('answer'), 'empty assistant answer'
print(json.dumps(parsed))
")
log "{\"step\":\"chat_turn_1\",\"parsed\":$PARSED1}"

CONV_ID=$(echo "$PARSED1" | python3 -c "import sys,json; print(json.load(sys.stdin)['conversation_id'])")

# 6. Follow-up (turn 2)
CHAT2=$(curl -sN -X POST "$API/chat" -H 'Content-Type: application/json' \
  -d "{\"conversation_id\":\"$CONV_ID\",\"message\":\"Can you elaborate on why doing a job well for its own sake matters for Sennett?\"}")
PARSED2=$(parse_sse "$CHAT2" "
import json
assert parsed.get('answer'), 'empty follow-up answer'
print(json.dumps({'answer': parsed['answer'][:500]}))
")
log "{\"step\":\"chat_turn_2\",\"parsed\":$PARSED2}"

# 7. Craftsman corpus sanity (optional — warn if missing)
CRAFT=$(curl -s "$API/documents/$CRAFTSMAN_ID")
log "{\"step\":\"craftsman_doc\",\"response\":$CRAFT}"
echo "$CRAFT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if d.get('status') != 'indexed':
    print('WARN: Craftsman doc not indexed', d.get('status'), file=sys.stderr)
    sys.exit(0)
assert d.get('chunk_count', 0) >= 100, 'Craftsman chunk count unexpectedly low'
print('craftsman_ok', d.get('chunk_count'))
" || fail "Craftsman sanity check failed"

log "{\"step\":\"complete\",\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"verdict\":\"pass\"}"
echo "DOGFOOD PASS — evidence: $OUT"
