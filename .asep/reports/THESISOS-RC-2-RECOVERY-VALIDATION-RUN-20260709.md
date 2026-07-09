# RC-2 Recovery Validation — Automated Run Log

> **Date:** 2026-07-09T20:58–21:05 UTC  
> **Environment:** Docker Compose @ `127.0.0.1:3000` / `127.0.0.1:8000`  
> **Script:** `bin/beta-validator-rc.sh` · extended route sweep (Beta V3 matrix)

## Verdict: **PASS** (automated Docker)

## Commands executed

```bash
make beta-validator-rc
make ap001-guard && make ap002-guard
# Extended route sweep (14 routes)
# API probes: /chapters, /conversations, /knowledge/concepts
```

## `make beta-validator-rc`

| Check | Result |
|-------|--------|
| `GET /health` | ✓ `{"status":"ok"}` |
| HTTP 6 surfaces | ✓ 200 all |
| Context API | ✓ |
| Playwright px1-context-api | ✓ 2/2 |
| **VERDICT** | **PASS** |

## Extended HTTP matrix (Beta V3 parity)

| Route | Status | fetch failed | Error banners | Content signal |
|-------|--------|--------------|---------------|----------------|
| `/` | 200 | 0 | 0 | OK |
| `/research` | 200 | 0 | 0 | OK |
| `/research/canvas` | 200 | 0 | 0 | canvas route OK |
| `/research/guided` | 200 | 0 | 0 | placeholder |
| `/writing` | 200 | 0 | 0 | writing-workspace |
| `/sources` | 200 | 0 | 0 | OK |
| `/sources/upload` | 200 | 0 | 0 | OK |
| `/knowledge` | 200 | 0 | 0 | Aura, Abbigliamento, 7 concepts |
| `/knowledge/graph` | 200 | 0 | 0 | was 500 in V3 |
| `/settings` | 200 | 0 | 0 | OK |
| `/review` | 200 | 0 | 0 | OK |
| `/ai` | 200 | 0 | 0 | ai-page shell |
| `/library` | 307 | — | — | redirect |
| `/workspace` | 307 | — | — | redirect |

## API backend

| Endpoint | Result |
|----------|--------|
| `/chapters` | ✓ JSON array with "Craftsmanship (dogfood M6)" |
| `/conversations?project_id=thesis-agent` | ✓ items including "M7 dogfood" |
| `/projects/thesis-agent/context?surface=home` | ✓ (Playwright) |

## Guards

| Guard | Result |
|-------|--------|
| `ap001-guard` | PASS |
| `ap002-guard` | PASS |

## Not run (human Beta Validation 2)

- Browser click-through (60+ interactive elements from V2)
- Cloudflare tunnel / public URL (AP-004)
- "+ Nuovo progetto" crash regression (C7)
- Chapter creation flow (C5)
- Usability questionnaire

## Report

Full comparison: `.asep/reports/THESISOS-RC-2-RECOVERY-VALIDATION.md`
