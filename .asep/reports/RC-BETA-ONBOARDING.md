# RC Beta Onboarding — ThesisOS v2.0.0-rc.1

> **Audience:** beta testers (5–10)  
> **Baseline:** `v2.0.0-rc.1` @ `fd23ad70`  
> **Phase:** validation only — no new features

## Access (public beta — attivo)

**URL da condividere:**

### https://indexes-ghz-joan-stronger.trycloudflare.com

Frontend + API sulla stessa origine (nginx + Cloudflare Tunnel).  
Funziona da qualsiasi browser, senza SSH.

> Il tunnel quick Cloudflare **non ha uptime garantito** e l’URL cambia se riavvii
> `bin/beta-public-open.sh`. Per ripristinare: `bash bin/beta-public-open.sh`

### Ripristino / rigenerazione URL

```bash
bash bin/beta-public-open.sh
cat /tmp/thesisos-beta-public.env   # URL corrente
```

### Opzioni alternative (solo dev)

<details>
<summary>SSH / Cursor port forward (single-user)</summary>

### Option A — Cursor

1. Remote-SSH → `thesisos-dev.europe-west1-b.thesisos-prod`
2. Forward ports **3000** + **8000**
3. http://localhost:3000

### Option B — SSH tunnel

```bash
gcloud compute ssh thesisos-dev --zone=europe-west1-b --project=thesisos-prod \
  -- -L 3000:127.0.0.1:3000 -L 8000:127.0.0.1:8000 -N
```

</details>

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
