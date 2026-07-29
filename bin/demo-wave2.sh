#!/usr/bin/env bash
# Wave 2 demo polish — strip migration prefixes from chapter titles, remove leftover dogfood.
# Usage:
#   bash bin/demo-wave2.sh --dry-run
#   bash bin/demo-wave2.sh --apply
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

API="${THESISOS_API:-http://localhost:8000}"
PROJECT="${THESISOS_PROJECT_ID:-thesis-agent}"

# Leftover test chapter not caught in Wave 1 cleanup
DELETE_CHAPTER_IDS=(
  12c5fecb-ab0a-4794-8d98-e90a58254982  # M7 dogfood chapter
)

DRY_RUN=1
for arg in "$@"; do
  case "$arg" in
    --apply) DRY_RUN=0 ;;
    --dry-run) DRY_RUN=1 ;;
    -h|--help)
      sed -n '2,6p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      exit 1
      ;;
  esac
done

echo "=== ThesisOS demo Wave 2 (project=$PROJECT) ==="
echo "Mode: $([[ "$DRY_RUN" -eq 1 ]] && echo DRY-RUN || echo APPLY)"
echo

if ! curl -sf "$API/health" >/dev/null 2>&1; then
  echo "API not reachable at $API — start stack: make up"
  exit 1
fi

fail=0

rename_chapters() {
  API="$API" PROJECT="$PROJECT" DRY_RUN="$DRY_RUN" python3 <<'PY'
import json
import os
import re
import sys
import urllib.error
import urllib.request

api = os.environ["API"]
project = os.environ["PROJECT"]
dry_run = os.environ.get("DRY_RUN", "1") == "1"
prefix_re = re.compile(r"^\[kimi-claw-[0-9-]+\]\s*")

def request(method, path, body=None):
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{api}{path}", data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        if resp.status == 204:
            return None
        return json.load(resp)

chapters = request("GET", f"/chapters?project_id={project}")
pending = []
for chapter in chapters:
    title = chapter.get("title") or ""
    if not prefix_re.match(title):
        continue
    new_title = prefix_re.sub("", title, count=1).strip()
    if not new_title or new_title == title:
        continue
    pending.append((chapter["id"], title, new_title, chapter["version"]))

print(f"--- Rename chapters ({len(pending)} pending) ---")
if not pending:
    print("  (none pending)")
else:
    for chapter_id, old_title, new_title, version in pending:
        if dry_run:
            print(f"  [dry-run] {chapter_id[:8]}…")
            print(f"            {old_title[:60]}")
            print(f"         -> {new_title[:60]}")
            continue
        try:
            request(
                "PATCH",
                f"/chapters/{chapter_id}?project_id={project}",
                {"title": new_title, "expected_version": version},
            )
            print(f"  OK    {chapter_id[:8]}… -> {new_title[:55]}")
        except urllib.error.HTTPError as exc:
            print(f"  FAIL  {chapter_id} HTTP {exc.code}", file=sys.stderr)
            sys.exit(1)
PY
}

delete_chapters() {
  echo "--- Delete leftover chapters (${#DELETE_CHAPTER_IDS[@]} in list) ---"
  mapfile -t EXISTING_CHAPTER_IDS < <(curl -sf "${API}/chapters?project_id=${PROJECT}" | python3 -c "
import json, sys
items = json.load(sys.stdin)
for item in items:
    print(item['id'])
" 2>/dev/null || true)
  pending=()
  for id in "${DELETE_CHAPTER_IDS[@]}"; do
    for existing in "${EXISTING_CHAPTER_IDS[@]}"; do
      if [[ "$existing" == "$id" ]]; then
        pending+=("$id")
        break
      fi
    done
  done
  if [[ ${#pending[@]} -eq 0 ]]; then
    echo "  (none pending)"
    return 0
  fi
  for id in "${pending[@]}"; do
    if [[ "$DRY_RUN" -eq 1 ]]; then
      echo "  [dry-run] DELETE chapter $id"
      continue
    fi
    code="$(curl -s -o /dev/null -w '%{http_code}' -X DELETE \
      "$API/chapters/${id}?project_id=${PROJECT}")"
    case "$code" in
      204) echo "  OK    chapter $id" ;;
      404) echo "  SKIP  chapter $id (already gone)" ;;
      *) echo "  FAIL  chapter $id HTTP $code" >&2; fail=1 ;;
    esac
  done
}

rename_chapters || fail=1
delete_chapters

echo
if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "Dry-run complete. Apply with: bash bin/demo-wave2.sh --apply"
else
  echo "Apply complete. Verify titles:"
  echo "  docker compose exec -T db psql -U thesisos -d thesisos -c \\"
  echo "    \"SELECT left(title,60) FROM chapters WHERE project_id='${PROJECT}' ORDER BY title;\""
fi

exit "$fail"
