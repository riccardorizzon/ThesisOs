# Branching Strategy

> Sources: `git branch`/`git tag` state, `docs/m0-promotion.md`, `docs/m1-promotion.md`, `.cursor/skills/orchestrate-builders/SKILL.md`, the `finishing-a-development-branch` skill.

## Model: milestone branches → `main`, tagged per milestone

```text
main  ──●(m0-complete)────────────────●(m1-complete, pending)──► …
         \                            /
          m0-foundations    m1-conversation-system
                                  \
                                   builder/<epic>-<packet>  (per-implementer worktrees)
```

## Branches
- **`main`** — promoted, gated milestones only. Tagged at each promotion.
- **`m{n}-<name>`** — the working branch for milestone N (e.g. `m0-foundations`,
  `m1-conversation-system`). All milestone work happens here until its gate is green.
- **`builder/<epic>-<packet>`** — short-lived implementer branches checked out into
  isolated git worktrees (`.worktrees/packet-<id>/`, gitignored). Merged back at the
  wave sync barrier (`git merge --no-ff`), then deleted.

## Current state (as of this knowledge build)
- Branches: `main`, `m0-foundations`, `m1-conversation-system` (current HEAD).
- Tags: `m0-complete`. `m1-complete` **not yet created** (cloud promotion pending).

## Promotion procedure (per milestone)
```bash
# only after the gate YAML is fully green + evidence recorded
git checkout main
git merge --no-ff m{n}-<name>
git tag m{n}-complete
# release: vX.Y.Z-m{n}  (M0 → v0.0.1-m0, M1 → v0.0.2-m1)
```
Then — and only then — start the next milestone (no parallel work before the tag,
to avoid contract drift).

## Worktree rules (parallel builds)
- One worktree per implementer packet per wave; never two implementers in one tree.
- Merge worktree branches only after `required_checks` pass.
- Remove the worktree + delete the branch after merge.

## Commit conventions
Conventional commits scoped to the milestone: `feat(m1):`, `fix(m1):`,
`contracts(m1):`, `docs(m1):`, `build(m1):`, `chore(m1):`, `merge(builder):`.

## Git safety
- Never force-push `main`; never amend/rewrite pushed history.
- `*.tfstate`, `.env`, `.impeccable/`, `.worktrees/`, `*.tsbuildinfo` are gitignored.
