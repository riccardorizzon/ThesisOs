#!/usr/bin/env bash
# Expose ThesisOS publicly via Cloudflare quick tunnel + nginx (single URL).
# Same-origin API — no GCP firewall required. For short beta sessions only.
#
# Reuse an existing tunnel URL (no cloudflared restart):
#   BETA_PUBLIC_URL=https://your.trycloudflare.com bash bin/beta-public-open.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CF="${CLOUDFLARED_BIN:-/tmp/cloudflared}"
NGINX_CONF="${ROOT}/infra/dev-vm/nginx-beta-public.conf"
STATE="/tmp/thesisos-beta-public.env"
LOG="/tmp/cloudflared-beta-public.log"

if [ ! -x "$CF" ]; then
  curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o "$CF"
  chmod +x "$CF"
fi

# nginx on :8080
sudo cp "$NGINX_CONF" /etc/nginx/sites-available/thesisos-beta-public
sudo ln -sf /etc/nginx/sites-available/thesisos-beta-public /etc/nginx/sites-enabled/thesisos-beta-public
sudo nginx -t
sudo systemctl reload nginx || sudo nginx -s reload

PUBLIC_URL="${BETA_PUBLIC_URL:-}"
if [ -z "$PUBLIC_URL" ] && [ -f "$STATE" ]; then
  # shellcheck disable=SC1090
  source "$STATE" 2>/dev/null || true
  PUBLIC_URL="${PUBLIC_URL:-}"
fi

if [ -n "$PUBLIC_URL" ]; then
  echo "Reusing PUBLIC_URL=$PUBLIC_URL (set BETA_PUBLIC_URL to override)"
  if ! pgrep -f 'cloudflared tunnel --url http://127.0.0.1:8080' >/dev/null 2>&1; then
    echo "cloudflared not running — starting tunnel (URL may change; set BETA_PUBLIC_URL if needed)"
    nohup "$CF" tunnel --url http://127.0.0.1:8080 --no-autoupdate >"$LOG" 2>&1 &
    for _ in $(seq 1 30); do
      DISCOVERED=$(rg -o 'https://[a-z0-9-]+\.trycloudflare\.com' "$LOG" | tail -1 || true)
      [ -n "$DISCOVERED" ] && PUBLIC_URL="$DISCOVERED" && break
      sleep 1
    done
  fi
else
  pkill -f 'cloudflared tunnel --url http://127.0.0.1:8080' 2>/dev/null || true
  sleep 1
  nohup "$CF" tunnel --url http://127.0.0.1:8080 --no-autoupdate >"$LOG" 2>&1 &
  for _ in $(seq 1 30); do
    PUBLIC_URL=$(rg -o 'https://[a-z0-9-]+\.trycloudflare\.com' "$LOG" | tail -1 || true)
    [ -n "$PUBLIC_URL" ] && break
    sleep 1
  done
fi

[ -n "$PUBLIC_URL" ] || { echo "tunnel URL not found; see $LOG"; exit 1; }

echo "PUBLIC_URL=$PUBLIC_URL" | tee "$STATE"
echo "GIT_COMMIT=$(git -C "$ROOT" rev-parse HEAD)" | tee -a "$STATE"
echo "GIT_TAG=$(git -C "$ROOT" describe --tags --always 2>/dev/null || true)" | tee -a "$STATE"

# Rebuild frontend in repo root — browser API calls use public same-origin URL (AP-004)
cd "$ROOT"
export NEXT_PUBLIC_API_BASE_URL="$PUBLIC_URL"
docker compose build frontend --build-arg "NEXT_PUBLIC_API_BASE_URL=$PUBLIC_URL"
docker compose up -d

sleep 5
curl -sf "$PUBLIC_URL/health" >/dev/null
curl -sf -o /dev/null -w '%{http_code}\n' "$PUBLIC_URL/" | grep -q 200

cat <<EOF

=== ThesisOS public beta URL (AP-004) ===
App:     $PUBLIC_URL
API:     $PUBLIC_URL  (same origin via nginx → backend :8000)
Commit:  $(git -C "$ROOT" rev-parse --short HEAD)

Tunnel log: $LOG
State:      $STATE
EOF
