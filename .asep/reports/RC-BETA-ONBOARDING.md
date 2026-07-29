# RC Beta Onboarding — ThesisOS v2.0.0-rc.2

> **Audience:** beta testers (5–10)  
> **Baseline:** `v2.0.0-rc.2` @ `5039df77` (M7 complete)  
> **Phase:** validation only — no new features (M8 blocked until beta exit)

## Access

### Local / dev VM (recommended for first cohort)

```bash
git checkout v2.0.0-rc.2   # or main @ 5039df77+
make up
# Frontend: http://localhost:3000
# API:      http://localhost:8000
```

Cursor Remote-SSH: forward ports **3000** + **8000**.

### Public beta (optional — short sessions)

Regenerate Cloudflare tunnel URL:

```bash
bash bin/beta-public-open.sh
cat /tmp/thesisos-beta-public.env   # URL corrente
```

> Quick tunnel has **no uptime SLA**; URL changes on restart.

<details>
<summary>Previous rc.1 public URL (deprecated)</summary>

`https://indexes-ghz-joan-stronger.trycloudflare.com` — superseded by rc.2 baseline.

</details>

Use Chrome or Firefox desktop. Research Canvas requires viewport ≥ 1024px.

## What to test (30–45 min)

1. **Home** — default route, resume card, coach marks on first visit
2. **Writing** — outline, editor, AI panel
3. **Manoscritto** (`/manuscript`) — ordered read-only thesis view
4. **Sources** — browse, open a source
5. **Knowledge** — explorer, concept card
6. **Research** — hub + **Canvas** (`/research/canvas`)
7. **Settings** — project prefs, export options, **beta limitations** panel

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

Triage tracker: `.asep/reports/THESISOS-v2.0.0-rc.2-BETA-VALIDATION.md`

## Known limitations (accepted for RC)

- **In-app (human):** Settings → *Beta — limitazioni note* (4 bullets)
- **Demo handout:** `docs/demo/DEMO-HANDOUT.md`
- **Technical:** `docs/KNOWN_LIMITATIONS.md` — especially L-01…L-05 in RC bundle §5.

## Validator (ops)

Re-run automated checks:

```bash
make demo-gate          # ops-check + Wave 1/2 data polish gates
make beta-validator-rc  # RC bundle validator
# or: bash bin/beta-validator-rc.sh
```
