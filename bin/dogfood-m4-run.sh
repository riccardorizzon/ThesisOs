#!/usr/bin/env bash
# M4 recovery dogfood runner — captures evidence for dogfood-m4.md
set -euo pipefail
API="${API_BASE:-http://localhost:8000}"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
OUT="${1:-/tmp/dogfood-m4-evidence.jsonl}"

log() { echo "$1" | tee -a "$OUT"; }

: > "$OUT"
log "{\"step\":\"start\",\"ts\":\"$TS\",\"api\":\"$API\"}"

# 1. Upload
MD=$(mktemp --suffix=.md)
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
for i in $(seq 1 40); do
  DOC=$(curl -s "$API/documents/$DOC_ID")
  STATUS=$(echo "$DOC" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))")
  if [[ "$STATUS" == "indexed" || "$STATUS" == "failed" ]]; then
    log "{\"step\":\"index\",\"attempt\":$i,\"response\":$DOC}"
    break
  fi
  sleep 2
done

# 3. Retrieve
SEARCH=$(curl -s -X POST "$API/search" -H 'Content-Type: application/json' \
  -d "{\"query\":\"What is craftsmanship according to Sennett?\",\"limit\":5,\"document_ids\":[\"$DOC_ID\"]}")
log "{\"step\":\"search\",\"response\":$SEARCH}"

# 4. Memory (thesis context for grounding wire)
MEM=$(curl -s -X POST "$API/memory" -H 'Content-Type: application/json' \
  -d '{"kind":"thesis","content":"This thesis discusses Richard Sennett'\''s book The Craftsman and the ethics of skilled work.","pinned":true}')
log "{\"step\":\"memory\",\"response\":$MEM}"

# 5. Grounded chat (turn 1)
CHAT1=$(curl -sN -X POST "$API/chat" -H 'Content-Type: application/json' \
  -d "{\"message\":\"According to my uploaded document, how does Sennett define craftsmanship? Cite sources.\"}")
CONV=$(echo "$CHAT1" | python3 -c "
import sys,re,json
raw=sys.stdin.read()
conv=None
sources=[]
tokens=[]
for block in raw.split('\n\n'):
    lines=block.strip().split('\n')
    if len(lines)<2: continue
    ev=lines[0].split(': ',1)[-1]
    data=json.loads(lines[1].replace('data: ','',1))
    if ev=='done': conv=data.get('conversation_id')
    elif ev=='sources': sources=data.get('sources',[])
    elif ev=='token': tokens.append(data.get('text',''))
print(json.dumps({'conversation_id':conv,'sources_count':len(sources),'answer':''.join(tokens),'sources':sources[:3]}))
")
log "{\"step\":\"chat_turn_1\",\"raw_events\":\"truncated\",\"parsed\":$CHAT1}" 2>/dev/null || true
log "{\"step\":\"chat_turn_1\",\"parsed\":$CONV}"

# 6. Follow-up (turn 2)
CONV_ID=$(echo "$CONV" | python3 -c "import sys,json; print(json.load(sys.stdin).get('conversation_id') or '')")
if [[ -n "$CONV_ID" ]]; then
  CHAT2=$(curl -sN -X POST "$API/chat" -H 'Content-Type: application/json' \
    -d "{\"conversation_id\":\"$CONV_ID\",\"message\":\"Can you elaborate on why doing a job well for its own sake matters for Sennett?\"}")
  PARSED2=$(echo "$CHAT2" | python3 -c "
import sys,re,json
raw=sys.stdin.read()
tokens=[]
for block in raw.split('\n\n'):
    lines=block.strip().split('\n')
    if len(lines)<2: continue
    if lines[0].endswith('token'):
        data=json.loads(lines[1].replace('data: ','',1))
        tokens.append(data.get('text',''))
print(json.dumps({'answer':''.join(tokens)}))
")
  log "{\"step\":\"chat_turn_2\",\"parsed\":$PARSED2}"
fi

# Craftsman full markdown sanity
CRAFTSMAN_ID="c31abf2c-a069-4919-b7fb-5eeb6cbebc19"
CRAFT=$(curl -s "$API/documents/$CRAFTSMAN_ID")
log "{\"step\":\"craftsman_doc\",\"response\":$CRAFT}"

log "{\"step\":\"complete\",\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
echo "Evidence written to $OUT"
rm -f "$MD"
