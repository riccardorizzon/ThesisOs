# RC Beta Onboarding — ThesisOS v2.0.0-rc.1

> **Audience:** beta testers (5–10)  
> **Baseline:** `v2.0.0-rc.1` @ `fd23ad70`  
> **Phase:** validation only — no new features

## Access

> **Important:** the dev VM is **not** exposed on the public internet (by design —
> see `infra/dev-vm/README.md`). Use **SSH port forwarding** or **Cursor Ports**.

### Option A — Cursor (recommended)

1. Connected via **Remote-SSH** to `thesisos-dev.europe-west1-b.thesisos-prod`
2. Open **Ports** panel (or Forward a Port)
3. Forward **3000** and **8000**
4. Open **http://localhost:3000**

### Option B — SSH tunnel from Mac

```bash
gcloud compute ssh thesisos-dev --zone=europe-west1-b --project=thesisos-prod \
  -- -L 3000:127.0.0.1:3000 -L 8000:127.0.0.1:8000 -N
```

Then open **http://localhost:3000** (keep the terminal open).

### Option C — Public beta (requires GCP admin)

Only if you explicitly open the firewall (not default):

```bash
gcloud compute firewall-rules create thesisos-rc-beta \
  --project=thesisos-prod \
  --direction=INGRESS \
  --priority=1000 \
  --network=default \
  --action=ALLOW \
  --rules=tcp:3000,tcp:8000 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=thesisos-dev
```

Then tag the VM and use `http://34.79.238.160:3000`. **Prefer Options A/B for single-user / internal beta.**

| Service | Local (via tunnel) | Public (only if firewall open) |
|---------|-------------------|----------------------------------|
| App | http://localhost:3000 | http://34.79.238.160:3000 |
| API | http://localhost:8000/health | http://34.79.238.160:8000/health |

Use Chrome or Firefox desktop. Research Canvas requires viewport ≥ 1024px.

## What to test (30–45 min)

1. **Home** — default route, resume card
2. **Writing** — outline, editor, AI panel
3. **Sources** — browse, open a source
4. **Knowledge** — explorer, concept card
5. **Research** — hub + **Canvas** (`/research/canvas`)
6. **Settings** — project prefs, export options

## Report only

Please report **only**:

- bugs (something broken)
- crashes / blank screens
- regressions vs expected behaviour
- critical UX blockers

Do **not** request new features during RC — they go to v3 backlog.

## How to send feedback

Reply to Product Lead with:

```text
Surface: (Home | Writing | Sources | Knowledge | Research | Settings)
Severity: (blocker | major | minor)
Steps: 1… 2… 3…
Expected:
Actual:
Screenshot: (optional)
```

Triage tracker: `.asep/reports/THESISOS-v2.0.0-rc.1-BETA-VALIDATION.md`

## Known limitations (accepted for RC)

See `docs/KNOWN_LIMITATIONS.md` — especially L-01…L-05 in RC bundle §5.

## Validator (ops)

Re-run automated checks:

```bash
make beta-validator-rc
# or: bash bin/beta-validator-rc.sh
```
