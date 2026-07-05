# _inbox — raw import (immutable reference)

Drop the **raw Kimi Claw export** into `kimi-claw/` (drag-and-drop into Cursor).

## Rules (see `docs/kimi-to-thesisos-migration-runbook.md`)

- `kimi-claw/` is the **immutable source of truth**: never rename, edit, or move
  anything inside it. All processing happens on copies elsewhere.
- Do **not** delete the raw copy after sorting — it is kept for future audits.
- Derived/working artifacts (inventory, mapping, manifest, log) live in the
  sibling `_migration/` folder, created during Phase 1 — **not** here.
