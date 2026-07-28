#!/usr/bin/env bash
# Wave 1 demo data cleanup — remove test documents/chapters; protect seeded core corpus.
# Usage:
#   bash bin/demo-cleanup.sh --dry-run                         # preview pending deletes
#   bash bin/demo-cleanup.sh --apply                           # docs + chapters + link sources
#   bash bin/demo-cleanup.sh --apply --conversations           # also delete noise threads
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

API="${THESISOS_API:-http://localhost:8000}"
PROJECT="${THESISOS_PROJECT_ID:-thesis-agent}"

# --- Protected: seeded core (sources.document_id) — never delete ---
PROTECTED_DOC_IDS=(
  1b606520-2923-482e-9d04-c123b686dacf  # Outline-Master
  54daa0e8-2922-4692-b750-9580daa885bd  # Stigmata-Framework
  9b35561b-0cf5-4ca3-83db-bc96262c4118  # Core-Theory-Map
  d9f074b6-79e5-4403-a6e6-7748d22b8556  # Sennett_The-Craftsman
  56e7fbe5-34eb-4d2e-b0cc-e220a5f515cf  # Benjamin
  e1114893-0a04-40c7-a15a-15d72ad8eb64  # Guida-Redazione-Tesi
)

KEEP_SECONDARY_DOC_IDS=(
  fcb97bcc-e3e4-4e34-92c7-a29f50159b77
  9e7eec1a-1187-48d4-8544-2b5980e62d1e
  aa23bef3-32f4-4723-acf0-7cf3cc09ee93
  0151175a-2a61-4095-b9c5-a86152151ed0
  1834a737-bf25-4cae-a400-b6bede6c8700
  95f2e49a-1384-4457-b57f-7e9348e23161
  1b3d08ec-fa6d-494b-a034-8aef8ac0e98f
  92bc3231-2729-4e41-8dd4-826179d8d38b
  13788fcb-385f-409c-b2aa-d53236932a5e
)

DELETE_DOC_IDS=(
  0634efb5-700a-4483-b034-b3ed945efbfe
  e7540d4e-b54e-4217-9d53-92cfba4b3f97
  8181860d-92ee-458e-b07f-d3af3743281f
  7f272196-516e-4060-9cf1-372444918599
  84ce8dc7-c774-48b7-8935-e6e7d1d4b37c
  a67ae3a2-7e24-4b84-a1b9-9f69cb03712c
  dea2ebee-edcd-4ab6-9324-7c1e9a453c4e
  1d2c6829-5077-4e8d-8a51-6601e92ef94e
  8246a26d-f148-4594-9f13-8e2edb968e19
  51f8adac-5798-489d-97a3-7fedab053532
  c31abf2c-a069-4919-b7fb-5eeb6cbebc19
  6013bd6f-9985-4be4-b0d4-28d969f78c43
  b85b16cc-2845-4598-99e0-83b95e662e8a
  07280808-82ee-49e6-b504-af8ad151fdc8
  e3b0b795-413d-4278-a044-31cb0ae8f4ca
  996b331f-77da-4f0a-bd7e-eefbaae41179
  de9df660-3e80-4216-b9ec-4e6aedd2a155
  fe90f8ea-f737-4528-9e5b-ffa231aaafd4
  2ff0f3e3-7bf2-47b4-82db-cf0f53e33d40
  5d049d53-9961-4241-a9dd-9bcaa6dec991
  aba29fac-a7d7-454b-832f-f350325c2975
  1f9cd742-71fb-4345-bae5-b60d94329738
  55c27c26-96c7-494a-91a0-c1634d97b7d0
  389384e7-8bf2-4edc-94d4-2752bb26750e
  a42ef5b9-3723-4888-9564-382fabdb8ac1
  cb252a04-5d39-42ba-bd1e-5f71f4f38a9b
  719006da-b6c8-43c0-b6f1-3e40b068d148
  72c05c34-6a62-438d-97e9-cc5f5430b798
  beb7c3a0-f8b4-470b-85da-faad96f1be99
  76306e6a-7ccc-40d3-9123-79197620dce3
  6dee07e6-8ae3-4dcd-901b-744c3beea37c
  6f801016-42d3-40f4-bc75-31157ee9d22f
  d7157920-e0fa-4bb1-bb7d-5134beea4026
  c592fe1d-beca-44c9-805e-0873c4600e6f
  f6011235-2fc0-481e-9c5d-ab4bc9850576
  0fe43d7d-27a0-4b1d-896c-d9eaf2fac6e6
  a2f166c8-c3f5-48cb-ac6d-1845366ac553
  0210544b-d42d-4ec9-ad23-701d0baa48d9
  c7f09391-2eeb-499c-aa88-3154ab9c3784
  38963f90-bad5-48eb-8ff2-bb03010af8df
  6a021144-dcff-45d5-9626-d9f46390d5b7
  42f065d0-7c8b-42bc-aadc-f0c27c0960ad
  20a4ffe4-f005-4b25-9af7-ffdf6f2a044c
  8cef87d0-a0a1-4d94-9b9b-285eddda79ca
  86d5d146-67a5-47d9-a514-e2837d66ae5a
  63462feb-f95d-47ef-8191-4a675be2fb9f
  51cf5ff8-f114-4211-ae01-da650f3169b2
  0eace74f-4794-43b8-b475-1f46e1a8d444
  bd6e5d04-e87d-4a1e-b062-6ae8b67cff58
  ea2f2838-70f6-446b-a3a6-22e9ab3b599e
  97ce9182-82cf-4437-a739-b8b2cf8aa592
)

# E2E/G5 noise (already removed in first apply; kept for idempotent re-run)
DELETE_CHAPTER_IDS=(
  c97085ac-5f2f-469f-9daf-4ec97879e4d6
  def76b59-bd21-4ad5-9df8-469f34c1d76d
  2ad647f2-0c97-4dee-88f0-aff1b6271b34
  3824aa41-1390-474d-8481-3a6d443398cb
  fe64f0f6-7a26-4cad-b025-e25577a48940
  c5c2639b-2ab7-4dc7-8941-ffe521f82aca
  a696a545-4f6b-4b75-b955-e87d230a9e15
  30c6bc7f-bf9e-41b3-9faa-711d519d0c9c
  0f11b036-a74e-409a-b143-909c317d0acf
)

# Empty duplicate stubs + test chapters (same title as filled review rows)
DELETE_EMPTY_CHAPTER_IDS=(
  fe01b674-250f-4662-9977-216e88182940  # Introduzione reti neurali sparse
  bfb9c3e4-2383-43ba-9bbd-c4983c847e33  # §1.1 stub
  3db78e45-04ea-4bd2-90a5-374e2418f7bd  # §1.2 stub
  08048a60-c3ee-42e8-bddf-8de67d67f36e  # §1.3 stub
  ab3f4c14-8af7-4c47-ad91-8753ec7ae4c3  # §2.1 stub
  4c0c888e-0ccb-4cc1-96dc-5db9b579dbad  # §2.2 stub
  0536a410-7057-400a-b69c-cc8ece99dea6  # §2.3 stub
  e2772c4e-081b-40b0-8aff-014641c1b0b0  # §2.4 stub
  e8793790-88ef-4841-9495-369b9450f280  # Cap. 3 stub
  273017a7-86ce-4d3b-b0ea-6ccf59edbfe9  # prova
)

DRY_RUN=1
DO_CONVERSATIONS=0
DO_LINK_SOURCES=0

for arg in "$@"; do
  case "$arg" in
    --apply) DRY_RUN=0; DO_LINK_SOURCES=1 ;;
    --dry-run) DRY_RUN=1 ;;
    --conversations) DO_CONVERSATIONS=1 ;;
    --link-sources) DO_LINK_SOURCES=1 ;;
    -h|--help)
      sed -n '2,7p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      exit 1
      ;;
  esac
done

is_protected() {
  local id="$1"
  local x
  for x in "${PROTECTED_DOC_IDS[@]}"; do
    [[ "$x" == "$id" ]] && return 0
  done
  return 1
}

fetch_existing_ids() {
  local endpoint="$1"
  curl -sf "${API}/${endpoint}?project_id=${PROJECT}" | python3 -c "
import json, sys
raw = json.load(sys.stdin)
items = raw if isinstance(raw, list) else raw.get('items', raw.get('results', []))
for item in items:
    print(item['id'])
"
}

echo "=== ThesisOS demo cleanup (project=$PROJECT) ==="
echo "Mode: $([[ "$DRY_RUN" -eq 1 ]] && echo DRY-RUN || echo APPLY)"
echo

if ! curl -sf "$API/health" >/dev/null 2>&1; then
  echo "API not reachable at $API — start stack: make up"
  exit 1
fi

mapfile -t EXISTING_DOC_IDS < <(fetch_existing_ids "documents" || true)
mapfile -t EXISTING_CHAPTER_IDS < <(fetch_existing_ids "chapters" || true)

doc_exists() {
  local id="$1"
  local x
  for x in "${EXISTING_DOC_IDS[@]}"; do
    [[ "$x" == "$id" ]] && return 0
  done
  return 1
}

chapter_exists() {
  local id="$1"
  local x
  for x in "${EXISTING_CHAPTER_IDS[@]}"; do
    [[ "$x" == "$id" ]] && return 0
  done
  return 1
}

pending_docs=()
for id in "${DELETE_DOC_IDS[@]}"; do
  if is_protected "$id"; then
    echo "ERROR: protected doc in delete list: $id" >&2
    exit 1
  fi
  if doc_exists "$id"; then
    pending_docs+=("$id")
  fi
done

pending_chapters=()
for id in "${DELETE_CHAPTER_IDS[@]}" "${DELETE_EMPTY_CHAPTER_IDS[@]}"; do
  if chapter_exists "$id"; then
    pending_chapters+=("$id")
  fi
done

echo "Documents pending delete: ${#pending_docs[@]} (of ${#DELETE_DOC_IDS[@]} in list)"
echo "Chapters pending delete:  ${#pending_chapters[@]}"
echo "Protected core docs:      ${#PROTECTED_DOC_IDS[@]}"
echo "Keep secondary docs:      ${#KEEP_SECONDARY_DOC_IDS[@]}"
echo "Documents in workspace:   ${#EXISTING_DOC_IDS[@]}"
echo "Chapters in workspace:    ${#EXISTING_CHAPTER_IDS[@]}"
echo

delete_doc() {
  local id="$1"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "  [dry-run] DELETE document $id"
    return 0
  fi
  local code
  code="$(curl -s -o /dev/null -w '%{http_code}' -X DELETE \
    "$API/documents/${id}?project_id=${PROJECT}")"
  case "$code" in
    204) echo "  OK    document $id" ;;
    404) echo "  SKIP  document $id (already gone)" ;;
    *) echo "  FAIL  document $id HTTP $code" >&2; return 1 ;;
  esac
}

delete_chapter() {
  local id="$1"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "  [dry-run] DELETE chapter $id"
    return 0
  fi
  local code
  code="$(curl -s -o /dev/null -w '%{http_code}' -X DELETE \
    "$API/chapters/${id}?project_id=${PROJECT}")"
  case "$code" in
    204) echo "  OK    chapter $id" ;;
    404) echo "  SKIP  chapter $id (already gone)" ;;
    *) echo "  FAIL  chapter $id HTTP $code" >&2; return 1 ;;
  esac
}

fail=0

if [[ ${#pending_docs[@]} -gt 0 ]]; then
  echo "--- Documents ---"
  for id in "${pending_docs[@]}"; do
    delete_doc "$id" || fail=1
  done
else
  echo "--- Documents --- (none pending)"
fi

if [[ ${#pending_chapters[@]} -gt 0 ]]; then
  echo "--- Chapters ---"
  for id in "${pending_chapters[@]}"; do
    delete_chapter "$id" || fail=1
  done
else
  echo "--- Chapters --- (none pending)"
fi

if [[ "$DO_LINK_SOURCES" -eq 1 ]]; then
  echo "--- Link catalog sources → indexed documents ---"
  if ! docker compose ps db 2>/dev/null | rg -q 'Up'; then
    echo "  FAIL db not Up — cannot link sources" >&2
    fail=1
  elif [[ "$DRY_RUN" -eq 1 ]]; then
    docker compose exec -T db psql -U thesisos -d thesisos -At -c "
      SELECT s.title || ' → ' || COALESCE(d.title, doc_id)
      FROM (VALUES
        ('79f659bd-66c0-4e98-abd1-1f49bf4d3407', 'fcb97bcc-e3e4-4e34-92c7-a29f50159b77'),
        ('f97da3b3-d114-4d1c-b010-1cdd287352cb', '9e7eec1a-1187-48d4-8544-2b5980e62d1e'),
        ('9ecb3239-f1f8-4312-8895-31aac24afe39', 'aa23bef3-32f4-4723-acf0-7cf3cc09ee93'),
        ('76d1a06b-fc5e-4d4d-8c99-a94e654c6f26', '0151175a-2a61-4095-b9c5-a86152151ed0'),
        ('6f012fd7-8432-4365-b586-e685d5e3c4b2', '56e7fbe5-34eb-4d2e-b0cc-e220a5f515cf')
      ) AS m(source_id, doc_id)
      JOIN sources s ON s.id::text = m.source_id
      LEFT JOIN documents d ON d.id::text = m.doc_id
      WHERE s.project_id = '${PROJECT}' AND s.document_id IS NULL;
    " | while read -r line; do
      echo "  [dry-run] LINK $line"
    done
  else
    updated="$(docker compose exec -T db psql -q -U thesisos -d thesisos -At -c "
      WITH mapping(source_id, doc_id) AS (VALUES
        ('79f659bd-66c0-4e98-abd1-1f49bf4d3407'::uuid, 'fcb97bcc-e3e4-4e34-92c7-a29f50159b77'::uuid),
        ('f97da3b3-d114-4d1c-b010-1cdd287352cb'::uuid, '9e7eec1a-1187-48d4-8544-2b5980e62d1e'::uuid),
        ('9ecb3239-f1f8-4312-8895-31aac24afe39'::uuid, 'aa23bef3-32f4-4723-acf0-7cf3cc09ee93'::uuid),
        ('76d1a06b-fc5e-4d4d-8c99-a94e654c6f26'::uuid, '0151175a-2a61-4095-b9c5-a86152151ed0'::uuid),
        ('6f012fd7-8432-4365-b586-e685d5e3c4b2'::uuid, '56e7fbe5-34eb-4d2e-b0cc-e220a5f515cf'::uuid)
      )
      UPDATE sources s
      SET document_id = m.doc_id
      FROM mapping m
      WHERE s.id = m.source_id
        AND s.project_id = '${PROJECT}'
        AND s.document_id IS NULL
        AND EXISTS (SELECT 1 FROM documents d WHERE d.id = m.doc_id)
      RETURNING s.title;
    ")"
    if [[ -n "$updated" ]]; then
      while IFS= read -r title; do
        [[ -z "$title" ]] && continue
        echo "  OK    linked source: $title"
      done <<< "$updated"
    else
      echo "  SKIP  all catalog sources already linked"
    fi
  fi
fi

if [[ "$DO_CONVERSATIONS" -eq 1 ]]; then
  echo "--- Conversations (noise) ---"
  if ! docker compose ps db 2>/dev/null | rg -q 'Up'; then
    echo "  FAIL db not Up — cannot list conversations" >&2
    fail=1
  else
    mapfile -t conv_ids < <(docker compose exec -T db psql -U thesisos -d thesisos -At -c "
      SELECT id::text FROM conversations
      WHERE project_id = '${PROJECT}'
        AND title IS NOT NULL
        AND title <> '__companion_open__'
        AND (
          title IN ('ping', 'ops ping', 'test', 'ciao', 'Ciao')
          OR title ILIKE '%walkthrough%'
          OR title ILIKE '%dogfood%'
          OR title ILIKE 'rispondi soltanto%'
        );
    ")
    if [[ ${#conv_ids[@]} -eq 0 ]]; then
      echo "  (none pending)"
    fi
    for cid in "${conv_ids[@]}"; do
      [[ -z "$cid" ]] && continue
      if [[ "$DRY_RUN" -eq 1 ]]; then
        echo "  [dry-run] DELETE conversation $cid"
      else
        code="$(curl -s -o /dev/null -w '%{http_code}' -X DELETE \
          "$API/conversations/${cid}?project_id=${PROJECT}")"
        case "$code" in
          204) echo "  OK    conversation $cid" ;;
          404) echo "  SKIP  conversation $cid (already gone)" ;;
          *) echo "  FAIL  conversation $cid HTTP $code" >&2; fail=1 ;;
        esac
      fi
    done
  fi
fi

echo
if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "Dry-run complete. Apply with: bash bin/demo-cleanup.sh --apply --conversations"
else
  echo "Apply complete. Verify: make ops-check && bash bin/demo-cleanup.sh --dry-run"
fi

exit "$fail"
