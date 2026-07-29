#!/usr/bin/env bash
# Realistic demo walkthrough — simulates DEMO-SCRIPT.md against live stack.
# Usage: bash bin/demo-simulate.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

API="${THESISOS_API:-http://localhost:8000}"
FE="${THESISOS_FE:-http://localhost:3000}"
PROJECT="${THESISOS_PROJECT_ID:-thesis-agent}"
SHOWCASE="503c33f5-a3d8-40ee-adc0-3ff067747a17"
fail=0
step=0

ok() { echo "  OK  $*"; }
bad() { echo "  FAIL $*" >&2; fail=1; }
section() { step=$((step + 1)); echo; echo "=== Step $step: $* ==="; }

echo "=== ThesisOS demo simulation (project=$PROJECT) ==="
echo "API=$API FE=$FE"
echo "Script: docs/demo/DEMO-SCRIPT.md"

if ! curl -sf "$API/health" >/dev/null; then
  bad "API down — make up"
  exit 1
fi

# ---------------------------------------------------------------------------
section "Fonti — corpus curato (/sources)"
# ---------------------------------------------------------------------------
docs_json="$(curl -sf "${API}/documents?project_id=${PROJECT}")"
doc_count="$(python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d) if isinstance(d,list) else len(d.get('items',[])))" <<<"$docs_json")"
indexed="$(python3 -c "
import json,sys
d=json.load(sys.stdin)
items=d if isinstance(d,list) else d.get('items',[])
print(sum(1 for x in items if x.get('status')=='indexed'))
" <<<"$docs_json")"
core_hit="$(python3 -c "
import json,sys
need={'Outline-Master','Stigmata-Framework','Core-Theory-Map','Sennett_The-Craftsman','Benjamin_Opera-Arte-Riproducibilita','Guida-Redazione-Tesi'}
items=json.load(sys.stdin)
items=items if isinstance(items,list) else items.get('items',[])
titles={i.get('title','') for i in items}
# allow exact or contained
hit=sum(1 for n in need if any(n in t for t in titles))
print(hit)
" <<<"$docs_json")"

[[ "$doc_count" -ge 15 ]] && ok "documents=$doc_count" || bad "documents=$doc_count (want >=15)"
[[ "$indexed" -ge 15 ]] && ok "indexed=$indexed" || bad "indexed=$indexed"
[[ "$core_hit" -eq 6 ]] && ok "6 core titles present" || bad "core titles found=$core_hit/6"

src_json="$(curl -sf "${API}/sources?project_id=${PROJECT}" 2>/dev/null || curl -sf "${API}/bibliography?project_id=${PROJECT}" 2>/dev/null || echo '[]')"
# sources endpoint may vary
src_linked="$(docker compose exec -T db psql -U thesisos -d thesisos -At -c \
  "SELECT COUNT(*) FROM sources WHERE project_id='${PROJECT}' AND document_id IS NOT NULL;" 2>/dev/null || echo 0)"
[[ "$src_linked" -eq 11 ]] && ok "sources linked 11/11" || bad "sources linked=$src_linked"

fe_code="$(curl -s -o /dev/null -w '%{http_code}' "${FE}/sources")"
[[ "$fe_code" == "200" ]] && ok "FE /sources → 200" || bad "FE /sources → $fe_code"

# ---------------------------------------------------------------------------
section "Chat — crea conversazione + 3 prompt demo"
# ---------------------------------------------------------------------------
conv="$(curl -sf -X POST "${API}/conversations" \
  -H 'Content-Type: application/json' \
  -d "{\"project_id\":\"${PROJECT}\",\"title\":\"Demo — STIGMATA e Sennett\"}")"
conv_id="$(python3 -c "import json,sys; print(json.load(sys.stdin).get('id',''))" <<<"$conv")"
[[ -n "$conv_id" ]] && ok "created conversation $conv_id" || bad "conversation create failed"

stream_chat() {
  local msg="$1"
  local out="/tmp/demo_sim_chat_$$.txt"
  curl -sf -X POST "${API}/chat" \
    -H 'Content-Type: application/json' \
    -d "{\"message\":$(python3 -c "import json,sys; print(json.dumps(sys.argv[1]))" "$msg"),\"project_id\":\"${PROJECT}\",\"conversation_id\":\"${conv_id}\"}" \
    -o "$out"
  python3 - "$out" <<'PY'
import json, sys
raw = open(sys.argv[1], encoding="utf-8", errors="replace").read()
tokens, sources = [], []
for line in raw.splitlines():
    if not line.startswith("data:"):
        continue
    payload = line[5:].strip()
    if not payload:
        continue
    try:
        obj = json.loads(payload)
    except json.JSONDecodeError:
        continue
    if "text" in obj:
        tokens.append(obj["text"])
    if "document_title" in obj:
        sources.append(obj["document_title"])
    for s in obj.get("sources") or []:
        if isinstance(s, dict):
            sources.append(s.get("document_title") or s.get("title") or "")
        else:
            sources.append(str(s))
text = "".join(tokens)
print(f"LEN={len(text)}")
print("TEXT=" + text[:280].replace("\n", " "))
print("SOURCES=" + "|".join(sorted(set(s for s in sources if s))[:8]))
sys.exit(0 if len(text) >= 80 else 1)
PY
}

echo "--- Prompt 1: STIGMATA ---"
if out1="$(stream_chat "Cos'è STIGMATA nel mio corpus? Riassumi in 5 bullet usando solo le fonti caricate.")"; then
  echo "$out1" | sed 's/^/  /'
  echo "$out1" | rg -qi 'STIGMATA|Stigmata' && ok "prompt1 mentions STIGMATA" || bad "prompt1 missing STIGMATA signal"
  echo "$out1" | rg -qi 'Stigmata-Framework|Outline-Master|Core-Theory' && ok "prompt1 grounded sources" || bad "prompt1 weak sources"
else
  bad "prompt1 chat stream failed / short answer"
fi

echo "--- Prompt 2: Sennett craftsmanship ---"
if out2="$(stream_chat "Secondo Sennett, cosa distingue la pratica manuale (craftsmanship) dal lavoro astratto? Una risposta, due paragrafi.")"; then
  echo "$out2" | sed 's/^/  /'
  echo "$out2" | rg -qi 'Sennett|craft|pratica|artigian' && ok "prompt2 Sennett/craft signal" || bad "prompt2 missing craft signal"
else
  bad "prompt2 chat stream failed / short answer"
fi

echo "--- Prompt 3: quality control ---"
if out3="$(stream_chat "Quali autori del corpus NON hai usato in questa risposta e perché?")"; then
  echo "$out3" | sed 's/^/  /'
  len="$(echo "$out3" | rg -o 'LEN=[0-9]+' | cut -d= -f2)"
  [[ "${len:-0}" -ge 40 ]] && ok "prompt3 reflective answer (len=$len)" || bad "prompt3 too short"
else
  bad "prompt3 chat stream failed"
fi

fe_ai="$(curl -s -o /dev/null -w '%{http_code}' "${FE}/ai")"
[[ "$fe_ai" == "200" ]] && ok "FE /ai → 200" || bad "FE /ai → $fe_ai"

# ---------------------------------------------------------------------------
section "Scrittura — Cap. 3 vetrina + AI grounded"
# ---------------------------------------------------------------------------
ch="$(curl -sf "${API}/chapters/${SHOWCASE}?project_id=${PROJECT}")"
ch_title="$(python3 -c "import json,sys; print(json.load(sys.stdin).get('title',''))" <<<"$ch")"
ch_status="$(python3 -c "import json,sys; print(json.load(sys.stdin).get('status',''))" <<<"$ch")"
ch_wc="$(python3 -c "import json,sys; print(json.load(sys.stdin).get('word_count',0))" <<<"$ch")"
ch_content="$(python3 -c "import json,sys; print(json.load(sys.stdin).get('content_md') or '')" <<<"$ch")"

[[ "$ch_title" == "Cap. 3 — Progettazione metodologica" ]] && ok "title='$ch_title'" || bad "title='$ch_title'"
[[ "$ch_status" == "review" ]] && ok "status=review" || bad "status=$ch_status"
[[ "$ch_wc" -ge 3000 ]] && ok "word_count=$ch_wc" || bad "word_count=$ch_wc"
[[ "${#ch_content}" -ge 5000 ]] && ok "content_md chars=${#ch_content}" || bad "content too short"

# selection from chapter for expand action
selection="$(python3 -c "
import json,sys
c=json.load(sys.stdin).get('content_md') or ''
# pick a mid paragraph-ish slice
s=c[800:1400].strip()
print(s[:400] if s else c[:400])
" <<<"$ch")"

echo "--- Writing panel action: expand (Benjamin + Sennett transition) ---"
write_out="/tmp/demo_sim_write_$$.txt"
write_code="$(curl -s -o "$write_out" -w '%{http_code}' -X POST "${API}/writing/actions" \
  -H 'Content-Type: application/json' \
  -d "$(python3 -c "
import json,sys
print(json.dumps({
  'action': 'expand',
  'project_id': sys.argv[1],
  'chapter_id': sys.argv[2],
  'selection_text': sys.argv[3],
  'chapter_content': open('/dev/stdin').read() if False else sys.argv[4][:6000],
  'context_summary': 'Aggiungi un paragrafo di transizione che richiami Benjamin (aura) e Sennett (pratica), tono accademico italiano.',
}))
" "$PROJECT" "$SHOWCASE" "$selection" "${ch_content:0:6000}")")"

if [[ "$write_code" == "200" ]]; then
  write_text="$(python3 - "$write_out" <<'PY'
import json,sys
raw=open(sys.argv[1],encoding='utf-8',errors='replace').read()
tokens=[]
for line in raw.splitlines():
    if line.startswith('data:'):
        p=line[5:].strip()
        if not p: continue
        try: o=json.loads(p)
        except: continue
        if 'text' in o: tokens.append(o['text'])
        if 'proposal' in o and isinstance(o['proposal'], str): tokens.append(o['proposal'])
        if 'content' in o and isinstance(o['content'], str): tokens.append(o['content'])
print(''.join(tokens) if tokens else raw[:500])
PY
)"
  wlen="${#write_text}"
  [[ "$wlen" -ge 80 ]] && ok "writing expand produced text (len=$wlen)" || bad "writing expand too short (len=$wlen)"
  echo "  snippet: $(echo "$write_text" | tr '\n' ' ' | head -c 220)…"
  echo "$write_text" | rg -qi 'Benjamin|aura|Sennett|pratica|artigian' \
    && ok "writing grounded signal (Benjamin/Sennett/aura/pratica)" \
    || bad "writing missing grounded signal"
else
  bad "writing/actions HTTP $write_code"
  head -c 300 "$write_out"; echo
fi

fe_w="$(curl -s -o /dev/null -w '%{http_code}' "${FE}/writing")"
fe_m="$(curl -s -o /dev/null -w '%{http_code}' "${FE}/manuscript")"
[[ "$fe_w" == "200" ]] && ok "FE /writing → 200" || bad "FE /writing → $fe_w"
[[ "$fe_m" == "200" ]] && ok "FE /manuscript → 200" || bad "FE /manuscript → $fe_m"

# ---------------------------------------------------------------------------
section "Review + Export"
# ---------------------------------------------------------------------------
fe_r="$(curl -s -o /dev/null -w '%{http_code}' "${FE}/review")"
[[ "$fe_r" == "200" ]] && ok "FE /review → 200" || bad "FE /review → $fe_r"

export_file="/tmp/demo_sim_cap3.md"
export_code="$(curl -s -o "$export_file" -w '%{http_code}' \
  "${API}/export/chapters/${SHOWCASE}.md?project_id=${PROJECT}")"
[[ "$export_code" == "200" ]] && ok "export Cap.3 → 200 ($(wc -c <"$export_file") bytes)" || bad "export → $export_code"
rg -qi 'progettazione|metodolog' "$export_file" && ok "export contains Cap.3 content" || bad "export content missing"
no_proj="$(curl -s -o /dev/null -w '%{http_code}' "${API}/export/chapters/${SHOWCASE}.md")"
[[ "$no_proj" == "422" ]] && ok "export without project_id → 422" || bad "export no-project → $no_proj"

# ---------------------------------------------------------------------------
section "Research canvas (Wave 4 optional)"
# ---------------------------------------------------------------------------
fe_c="$(curl -s -o /dev/null -w '%{http_code}' "${FE}/research/canvas")"
[[ "$fe_c" == "200" ]] && ok "FE /research/canvas → 200" || bad "FE /research/canvas → $fe_c"

# ---------------------------------------------------------------------------
section "Limitazioni in Settings"
# ---------------------------------------------------------------------------
# Settings is client-rendered; verify FE loads and panel exists in source bundle via testid in built page or component file
if rg -q 'beta-limitations-panel' frontend/components/settings/BetaLimitationsPanel.tsx; then
  ok "BetaLimitationsPanel in product UI"
else
  bad "BetaLimitationsPanel missing"
fi
fe_s="$(curl -s -o /dev/null -w '%{http_code}' "${FE}/settings")"
[[ "$fe_s" == "200" ]] && ok "FE /settings → 200" || bad "FE /settings → $fe_s"

echo
if [[ "$fail" -eq 0 ]]; then
  echo "demo-simulate: PASS — percorso demo reale (fonti→chat→writing→export) OK"
  echo "Conversation demo: $conv_id"
  exit 0
else
  echo "demo-simulate: FAIL — vedi FAIL sopra" >&2
  exit 1
fi
