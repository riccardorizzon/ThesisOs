# Loop Budget — ASEP Builder Orchestration

Soft limits for unattended or long-running builder loops. Hard enforcement is
human + `/goal --tokens` + epic `close`.

## Session / epic caps

| Resource | Soft cap | Kill switch |
|----------|----------|-------------|
| Cursor Task agents per wave | ≤6 parallel implementers | Stop dispatch; run `sync` first |
| Waves per epic | Plan-defined (typically 2–4) | `orchestrate builders close` |
| Token budget (session goal) | `/goal --tokens 250K` default | `/goal pause` |
| Auto-fix attempts per blocker | 3 | Escalate to human (see `STATE.md`) |

## Daily (when running scheduled triage loops)

| Item | Cap |
|------|-----|
| Auto-PRs | 0 until L2 checklist + verifier agent wired |
| Sub-agent spawns (L1 triage) | 0 — report-only |

## Cost estimation

When Node is available:

```bash
npx @cobusgreyling/loop-cost
```

## Pause / kill

1. Set epic `status: paused` in `plans/builder/STATE.yaml` (convention)
2. `/goal pause` for session-scoped work
3. Do not advance `wave` until blockers cleared and checks green

## Log

Append each orchestration cycle to `loop-run-log.md`.
