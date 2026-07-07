# RC Staging Smoke — Evidence Report

> **Product:** ThesisOS v2.0.0-rc.1  
> **Deploy commit:** `fd23ad70` (exact — worktree `.worktrees/rc-staging`)  
> **Date:** 2026-07-07  
> **Environment:** local staging (`docker compose` @ ports 3000/8000)

## Deploy verification

| Check | Result |
|-------|--------|
| Worktree @ `fd23ad70` | ✓ |
| `docker compose up --build -d` | ✓ `rc-staging-*` containers |
| `GET /health` | ✓ `{"status":"ok"}` |
| Frontend HTTP | ✓ 200 @ `:3000` |

## RC validation smoke (6 surfaces)

Playwright against running stack (`PLAYWRIGHT_SKIP_WEBSERVER=1`):

| Surface | Route | Result |
|---------|-------|--------|
| Home | `/` | ✓ PASS |
| Writing | `/writing` | ✓ PASS (`writing-workspace`) |
| Knowledge | `/knowledge` | ✓ PASS |
| Sources | `/sources` | ✓ PASS |
| Research Canvas | `/research/canvas` | ✓ PASS (`research-canvas-shell`) |
| Settings | `/settings` | ✓ PASS (`settings-page`) |

**Verdict:** 6/6 PASS

## Notes

- Legacy `px1-ui-smoke.spec.ts` Writing test expects `writing-editor-placeholder` (removed in product); RC smoke uses `writing-workspace` only.
- PX-1 smoke: 4/5 PASS (Writing placeholder drift — non-blocking for RC).

## WO-TRACE

```text
RC APPROVED → governance commit b052df67 → staging @ fd23ad70 → smoke 6/6 PASS → beta validation
```
