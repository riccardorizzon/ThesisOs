#!/usr/bin/env bash
# Expose RC staging publicly via Cloudflare quick tunnel + nginx (single URL).
# Same-origin API — no GCP firewall required. For short beta sessions only.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RC="${ROOT}/.worktrees/rc-staging"
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

pkill -f 'cloudflared tunnel --url http://127.0.0.1:8080' 2>/dev/null || true
sleep 1
nohup "$CF" tunnel --url http://127.0.0.1:8080 --no-autoupdate >"$LOG" 2>&1 &
for _ in $(seq 1 30); do
  PUBLIC_URL=$(rg -o 'https://[a-z0-9-]+\.trycloudflare\.com' "$LOG" | tail -1 || true)
  [ -n "$PUBLIC_URL" ] && break
  sleep 1
done
[ -n "$PUBLIC_URL" ] || { echo "tunnel URL not found; see $LOG"; exit 1; }

echo "PUBLIC_URL=$PUBLIC_URL" | tee "$STATE"

# Rebuild frontend @ RC baseline with same-origin API URL
cp "$ROOT/docker/frontend.Dockerfile" "$RC/docker/frontend.Dockerfile"
cd "$RC"
docker compose build frontend --build-arg "NEXT_PUBLIC_API_BASE_URL=$PUBLIC_URL"
docker compose up -d frontend

sleep 3
curl -sf "$PUBLIC_URL/health" >/dev/null
curl -sf -o /dev/null -w '%{http_code}\n' "$PUBLIC_URL/" | grep -q 200

cat <<EOF

=== ThesisOS RC — public beta URL ===
App:  $PUBLIC_URL
API:  $PUBLIC_URL  (same origin via nginx)

Tunnel log: $LOG
State:      $STATE
EOF
