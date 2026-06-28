#!/usr/bin/env bash
# M5 Runtime Qualification dogfood — exercises the orchestrated runtime over /chat.
#
# Conversation route (no retrieval) + grounded route (upload → ask), asserting the
# user always receives a reply and the grounded turn streams sources. Records a
# coarse latency benchmark (B_lat conversation, B_ground grounded).
#
# Requires a running stack (make up) and Vertex ADC for embedding/chat.
#
# Usage:
#   bin/dogfood-m5-conversation-run.sh [evidence.jsonl]
#   make dogfood-m5
set -euo pipefail

API="${API_BASE:-http://localhost:8000}"
OUT="${1:-/tmp/dogfood-m5-evidence.jsonl}"

log() { echo "$1" >> "$OUT"; }
fail() { echo "DOGFOOD M5 FAIL: $*" >&2; exit 1; }

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
log "{\"step\":\"start\",\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"api\":\"$API\"}"

# 1. Conversation route — no retrieval; must still reply.
T0=$(date +%s.%N)
CHAT=$(curl -sN -X POST "$API/chat" -H 'Content-Type: application/json' \
  -d '{"message":"In one sentence, what is a thesis statement?"}')
B_LAT=$(echo "$(date +%s.%N) - $T0" | bc)
parse_sse "$CHAT" "
assert parsed.get('conversation_id'), 'missing conversation_id'
assert parsed.get('answer'), 'empty conversation answer'
assert parsed.get('sources_count', 0) == 0, 'conversation route should not retrieve'
print('conversation_ok')
" >/dev/null || fail "conversation route did not reply cleanly"
log "{\"step\":\"conversation\",\"b_lat_s\":$B_LAT}"

# 2. Grounded route — upload then ask about the document; must stream sources.
MD=$(mktemp --suffix=.md); trap 'rm -f "$MD"' EXIT
cat > "$MD" <<'EOF'
# Dogfood M5 — grounding excerpt
A thesis statement is a single sentence that states the central claim of an essay.
EOF
UPLOAD=$(curl -s -X POST "$API/upload" -F "file=@$MD;filename=dogfood_m5.md" -F "title=Dogfood M5 excerpt")
DOC_ID=$(echo "$UPLOAD" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
for i in $(seq 1 40); do
  STATUS=$(curl -s "$API/documents/$DOC_ID" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))")
  [[ "$STATUS" == "indexed" ]] && break
  [[ "$STATUS" == "failed" ]] && fail "indexing failed"
  sleep 2
done

T0=$(date +%s.%N)
CHAT_G=$(curl -sN -X POST "$API/chat" -H 'Content-Type: application/json' \
  -d '{"message":"According to my uploaded document, what is a thesis statement? Cite sources."}')
B_GROUND=$(echo "$(date +%s.%N) - $T0" | bc)
parse_sse "$CHAT_G" "
assert parsed.get('answer'), 'empty grounded answer'
assert parsed.get('sources_count', 0) > 0, 'grounded route missing sources'
print('grounded_ok')
" >/dev/null || fail "grounded route did not return sources"
log "{\"step\":\"grounded\",\"b_ground_s\":$B_GROUND}"

log "{\"step\":\"complete\",\"verdict\":\"pass\"}"
echo "DOGFOOD M5 PASS — evidence: $OUT (B_lat=${B_LAT}s, B_ground=${B_GROUND}s)"
