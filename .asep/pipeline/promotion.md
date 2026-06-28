# Promotion

Run only for intent=`promote` (or a capability with a `promotion` target reached).
Use `.asep/templates/promotion-template.md`.

Update automatically:

```text
Plan frozen-milestones table → Promotion doc → knowledge mirror → Runtime Contract (freeze) → tag
```

- Plan: add the milestone commit + baseline to the frozen-milestones table.
- Promotion doc: `docs/<milestone>-promotion.md` with the promotion-criteria yaml green.
- Knowledge mirror: `knowledge/architecture/*`, `knowledge/project/roadmap.md`.
- Runtime Contract: move from Draft → frozen if this milestone freezes it (M5.6).
- Capability graph: set the node `status: done` and record its `baseline`.
- Tag: create the milestone tag **only when the user explicitly asks**.

Gate: all qualification gates green (`.asep/pipeline/qualification.md`) before promoting.
