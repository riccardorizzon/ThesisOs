# PR draft — feat/companion-persistence (Writing Action Loop)

**Compare:** https://github.com/riccardorizzon/ThesisOs/compare/main...feat/companion-persistence

## Summary

- Add a **read-only tool loop** for Writing panel **Verifica** and **Trova fonti**: multi-step corpus search before draft generation (OpenWorker-inspired, domain-specific).
- **Riscrivi** / **Espandi** unchanged (legacy single-pass path).
- SSE **`step`** events + progress list in the AI panel for loop actions.
- ADR-0049, design spec, implementation plan, 32+ backend tests; `make ci` green.
- Live Vertex smoke verified: 2+ searches per verify/find-sources, HTTP SSE steps + token stream.

## Test plan

- [x] `make ci` (598 backend + 453 frontend + openapi-drift)
- [x] Live Docker smoke: `verify` / `find-sources` orchestrator + `POST /writing/actions` SSE
- [x] `WritingAiPanel` component tests (step UI for verify/find-sources only)
- [ ] Manual UI: open `/writing`, select chapter, run **Verifica** → see progress steps → Proposal queue
- [ ] Manual UI: **Riscrivi** → no step list, legacy behavior

## Key files

- `backend/app/runtime/action_loop/` — loop engine
- `backend/app/services/writing/action_loop_runner.py` — two-phase pipeline
- `backend/app/api/writing_actions.py` — action routing
- `frontend/components/writing/WritingAiPanel.tsx` — step progress UI

## Note

Branch contains additional companion/multi-thesis/demo work beyond this feature; review holistically or consider follow-up PRs if scope is too wide.
