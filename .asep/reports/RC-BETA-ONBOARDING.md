# RC Beta Onboarding — ThesisOS v2.0.0-rc.1

> **Audience:** beta testers (5–10)  
> **Baseline:** `v2.0.0-rc.1` @ `fd23ad70`  
> **Phase:** validation only — no new features

## Access

| Service | URL |
|---------|-----|
| App (staging) | http://34.79.238.160:3000 |
| API health | http://34.79.238.160:8000/health |

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
