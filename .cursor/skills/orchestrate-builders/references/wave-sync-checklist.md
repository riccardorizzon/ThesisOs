# Wave Sync Checklist

Run every `sync` between waves. Do not advance until all items pass.

## Collect

- [ ] Every `in_progress` packet has agent return recorded in STATE
- [ ] Status set to `done`, `blocked`, or re-dispatch planned
- [ ] `output`, `checks`, `integration_notes` filled for done packets

## Validate STATE

```bash
.cursor/skills/orchestrate-builders/scripts/validate-state.sh
```

- [ ] No overlapping `file_locks` for different packets
- [ ] No `in_progress` packet owns same path as another active packet
- [ ] All `depends_on` reference existing packet IDs
- [ ] Done dependencies satisfied for packets advancing to next wave

## Merge (implementers)

For each done implementer with worktree:

- [ ] Branch exists: `builder/{epic}-{packet_id}`
- [ ] `git merge --no-ff` into main integration branch
- [ ] Conflicts resolved and noted in STATE if any
- [ ] Re-run packet `required_checks` after merge

## Wave checks

- [ ] All packet-level `required_checks` passed (pre-merge in worktree, post-merge in main)
- [ ] Wave-level checks from plan executed (if defined)
- [ ] No new violations of `decisions` in STATE

## Advance

- [ ] `file_locks` cleared
- [ ] `wave` incremented in STATE
- [ ] Next-wave packets marked `ready` where deps satisfied
- [ ] Worktrees removed for merged packets
- [ ] Merged builder branches deleted (optional, after successful merge)

## Blocked path

If any packet `blocked`:

- [ ] `blockers` entry in STATE with owner and resolution plan
- [ ] Wave NOT advanced until blocker resolved or packet cancelled
- [ ] User informed of blocker before next `wave`

## Final wave

- [ ] Integrator packet complete
- [ ] Full epic test matrix green
- [ ] STATE `status: closed` or handoff prepared
