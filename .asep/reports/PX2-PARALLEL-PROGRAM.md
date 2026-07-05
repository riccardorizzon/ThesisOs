# PX2 Parallel Engineering Program

> **Status:** COMPLETE — PX-2 qualified (QWO-PX2-001-R1 PASS 2026-07-04)  
> **Authorization:** RATIFIED  
> **Supervisor mode:** Engineering Supervisor — coordinates, does not implement  
> **Program:** `.asep/programs/thesisos-product-v2.yaml` + `.asep/programs/px2-parallel.yaml`

---

## Purpose

PX-2 completes through **parallel sub-agents** with **Integration Review barriers**
after each wave — catching merge issues before the next dispatch or QWO.

```text
Wave A → Integration A → Wave B → Integration B → Wave C → Integration C → Wave D → QWO
```

PX-1 is **frozen and qualified**. PX-2 **activates** existing shells — no IA redesign.

---

## Supervisor responsibilities

| Does | Does not |
|------|----------|
| Maintains Capability Graph | Write application code |
| Files / approves EWO Proposals | Change Product Constitution or ADRs |
| Assigns sub-agent ownership | Modify another EWO's forbidden paths |
| Sets merge order + wave barriers | Skip CI after merge |
| Integrates worktree merges | Auto-accept QWO PARTIAL |
| Runs QWO-PX2-001 | Redesign UX or product vision |

State machine: `.asep/governance/engineering-supervisor.md`

---

## Parallel graph

```text
                         Supervisor
                              │
        ┌──────────┬─────────┼─────────┬──────────┐
        │          │         │         │          │
   Wave A (parallel — disjoint ownership)
        │          │         │         │          │
   EWO-001    EWO-002    EWO-005       │          │
  ContextBar  Editor    Decisions      │          │
  Inspector   Lifecycle  Cards         │          │
        │          │         │         │          │
        └──────────┴────┬────┴─────────┘          │
                        │ merge barrier Wave A      │
        ┌───────────────┼───────────────┐           │
        │               │               │           │
   Wave B (parallel — after Wave A)
        │               │               │           │
   EWO-003        EWO-004        EWO-006           │
  AI + Props    Source+Cite    Session+Continua     │
        │               │               │           │
        └───────────────┴───────┬───────┘           │
                                │ merge barrier Wave B
                           EWO-007
                         Review workspace
                                │
                           EWO-008
                      Chrome + integration
                                │
                        QWO-PX2-001
                      PX-2 Qualification
```

---

## Sub-agent assignment

| EWO | Agent | Ownership summary |
|-----|-------|-------------------|
| PX2-EWO-001 | A | ContextBar live + ContextInspector |
| PX2-EWO-002 | B | MarkdownEditor + lifecycle + outline |
| PX2-EWO-003 | C | RightRail + AI panel + proposals |
| PX2-EWO-004 | D | SourcePicker + Reader + cite |
| PX2-EWO-005 | E | DecisionCard + amber warnings |
| PX2-EWO-006 | F | SessionChip + Continua + bundle |
| PX2-EWO-007 | G | ReviewCompare activation |
| PX2-EWO-008 | H | Command palette + states + integration | implemented |

---

## Dispatch gate

```text
[x] Product spec filed       — px2-research-workspace-experience.md
[x] UI spec filed            — px2-research-workspace-ui-spec.md
[x] EWO proposals filed      — PX2-EWO-001…008
[x] Program review draft     — ARCHITECT-PROGRAM-REVIEW-PX2.md
[ ] Amendment ratified       — EXECUTION-AUTHORIZATION-PX2-AMENDMENT.md
[x] Amendment ratified       — 2026-07-04
[x] Wave A dispatched        — PX2-WAVE-A-DISPATCH.md
[x] Integration B PASS       — PX2-INTEGRATION-B.md
[x] Wave C dispatched          — PX2-WAVE-C-DISPATCH.md
[x] Integration C PASS         — PX2-INTEGRATION-C.md
[x] Wave D dispatched          — PX2-WAVE-D-DISPATCH.md
[x] Integration D PASS         — PX2-INTEGRATION-D.md
[x] QWO-PX2-001 authorized     — operator 2026-07-05
[x] QWO-PX2-001-R1 PASS        — QWO-PX2-001-R1.md
[x] PX-2 FROZEN                — PX2-MILESTONE-DISPOSITION.md
[ ] PX-3 authorization         — WAIT (Gate 3 amendment required)
```

---

## WO-TRACE

```text
PX-1 COMPLETE → PX2 specs → PX2 EWO proposals → px2-parallel.yaml
  → (ratify amendment) → Wave A dispatch → … → QWO-PX2-001
```
