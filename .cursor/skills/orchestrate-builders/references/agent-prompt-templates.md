# Builder Agent Prompt Templates

Use when dispatching Task agents in a wave. Every prompt must be **self-contained**.

---

## Explorer Prompt

```markdown
# Builder Packet {ID} — Explorer

**Epic:** {epic}
**Wave:** {wave}
**Agent type:** explorer (read-only — do NOT modify production code)

## Repository
Full Repository Path: {main_repo_abs_path}

## Owned scope (read/analyze only)
{owned_files list}

## DO NOT touch
{do_not_touch list}

## Decisions (MUST respect)
{decisions from STATE.yaml — verbatim}

## Task
{objective from packet yaml}

## Reads
{reads list with paths}

## Return format
1. **Status:** DONE | BLOCKED | NEEDS_CONTEXT
2. **Summary** (5-8 bullets): intent map, coupling risks, recommended implementer split
3. **Candidate work packets** for next wave (non-overlapping owned_files)
4. **Validation commands** per suggested packet
5. **Integration notes** for Sync barrier
```

---

## Implementer Prompt (worktree)

```markdown
# Builder Packet {ID} — Implementer

**Epic:** {epic}
**Wave:** {wave}
**Agent type:** implementer

## Repository (ISOLATED WORKTREE — work here only)
Full Repository Path: {worktree_abs_path}

## Branch
builder/{epic}-{id}

## Owned files (ONLY these)
{owned_files list}

## DO NOT touch
{do_not_touch list}

## Decisions (MUST respect — violating = BLOCKED)
{decisions from STATE.yaml — verbatim}

## Dependency outputs (already completed)
{for each depends_on packet: id + output summary from STATE}

## Task
{objective from packet yaml}

## Invariants
{invariants from packet yaml}

## Required checks (run and report exact output)
{required_checks from packet yaml}

## Execution
1. Implement only this packet objective.
2. Preserve invariants and external behavior.
3. Run all required checks.
4. Self-review: spec gaps, files outside ownership.

## Return format
1. **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
2. **Summary** (3-5 bullets): what changed
3. **Checks:** command → result for each required check
4. **Changed files** (list)
5. **Integration notes** for Sync (merge risks, follow-ups)
```

---

## Reviewer Prompt (post-merge, main repo)

```markdown
# Builder Packet {ID} — Reviewer

**Epic:** {epic}
**Packet under review:** {implemented_packet_id}

## Repository
Full Repository Path: {main_repo_abs_path}

## Context
Review merged changes from packet {implemented_packet_id} after sync barrier.

## Decisions
{decisions from STATE}

## Spec reference
{plan/spec paths}

## Review stages (both required)
1. **Spec compliance** — matches packet objective and milestone spec? Nothing extra?
2. **Code quality** — patterns, tests, edge cases

## Return format
1. **Spec:** PASS | FAIL (with specific gaps)
2. **Quality:** PASS | FAIL (with issues ranked)
3. If FAIL: exact fixes required before packet stays `done`
```

---

## Integrator Prompt (final wave)

```markdown
# Builder Packet {ID} — Integrator

**Epic:** {epic}
**Wave:** {wave} (final)

## Repository
Full Repository Path: {main_repo_abs_path}

## Merged packets
{list all implementer packets with integration_notes}

## Task
{objective — typically: full test suite, OpenAPI diff, lint, conflict audit}

## Required checks
{wave-level and epic-level checks from plan}

## Return format
1. **Status:** DONE | BLOCKED
2. **Integration report:** conflicts resolved, test matrix results
3. **Residual risks** for handoff
4. **Recommended next epic** or follow-up packets
```

---

## Orchestrator Synthesis Prompt (planning, no Task)

```markdown
Merge explorer outputs into dependency-aware plan for STATE.yaml.

Explorer outputs:
{paste P1, P2, P3 summaries}

Produce:
1. Packet table: id · wave · agent_type · owned_files · depends_on
2. Parallel waves (no file overlap per wave)
3. decisions list for STATE (from plan anti-goals + ADRs)
4. Validation matrix (packet checks + wave checks + epic checks)
5. Risk list with mitigations
```
