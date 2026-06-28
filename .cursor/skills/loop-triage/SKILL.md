---
name: loop-triage
description: >-
  Daily builder-loop triage for ASEP. Read STATE.yaml via builder-engine observe,
  summarize ready/blockers, append to STATE.md watch list. Report-only unless
  user explicitly enables auto-fix with loop-verifier.
---

# Loop Triage (ASEP)

Run at the start of each builder session or on `/loop` schedule.

## Steps

1. **Observe** (read-only):

```bash
builder-engine observe --repo-root . --json
```

If unavailable: read `plans/builder/STATE.yaml` and run `validate-state.sh`.

2. **Summarize** in this format:

```markdown
## Triage — {date}
- Epic: {epic} · Wave {wave} · Status {epic_status}
- Ready: {ready_count} · In flight: {in_flight_count} · Blockers: {blockers}
- Git: {branch}, dirty={dirty}
- Stale: {staleness_reasons or "none"}
```

3. **Update** `STATE.md` → `Last run` timestamp and `Watch` section only.
   Do **not** edit `plans/builder/STATE.yaml` packet status in report-only mode.

4. **Append** one line to `loop-run-log.md`.

5. **Escalate** to human when:
   - `staleness_reasons` non-empty
   - open `blockers` in STATE
   - validation errors from `lint-graph`

## Auto-fix (L2+ only)

Only when the user explicitly requests action:

- Spawn implementer in an isolated worktree
- Run **loop-verifier** before marking work complete
- Max 3 attempts per blocker (see `loop-budget.md`)

## Do not

- Auto-merge PRs
- Edit frozen specs/ADRs/contracts
- Touch denylist paths in `docs/safety.md`
