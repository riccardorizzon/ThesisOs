---
name: loop-budget
description: >-
  Check loop spend limits at start/end of builder sessions. Read loop-budget.md
  and loop-run-log.md; warn or pause when caps exceeded.
---

# Loop Budget

At the **start** and **end** of each orchestration cycle:

1. Read `loop-budget.md` caps.
2. Count parallel dispatches in current wave (from `STATE.yaml` `in_progress`).
3. If over cap → recommend `/goal pause` or stop `wave` dispatch.
4. Append run to `loop-run-log.md` if not already logged this cycle.

## Kill switches

- `/goal pause` — session goal
- Epic paused in STATE (convention: document in blockers)
- User says "stop loop"

Do not auto-continue past soft token budget without user ack.
