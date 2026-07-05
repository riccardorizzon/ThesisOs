# Engineering WorkOrder Proposal — PX2-EWO-003

> **Status:** ⏳ **PROPOSED** — dispatch blocked until amendment ratified.
>
> Program: `.asep/programs/thesisos-product-v2.yaml`  
> Capability: `px2-ewo-003-ai-proposal-queue`  
> Spec: `docs/product/specs/px2-research-workspace-experience.md` §6.3, §15.3–15.4  
> UI: `design-system/thesisos/px2-research-workspace-ui-spec.md` §5.4

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX2-EWO-003 |
| **Sub-agent** | C |
| **Type** | **EWO** — Alignment |
| **EWO category** | **Alignment** |
| **Capability** | `px2-ewo-003-ai-proposal-queue` |
| **User capability** | **PX-2.2** Writing Flow |
| **Milestone** | PX-2 |
| **Layer** | Business (frontend) + Runtime (writer graph seam) |
| **Wave** | px2-parallel/wave_b |
| **Depends on** | PX2-EWO-001, PX2-EWO-002 |

---

## Objective

Activate **Writing AI panel** with selection-aware actions, **streaming responses**,
and **proposal queue** — Applica never silent-writes; all AI mutations go through
proposal flow per ADR-0039 and IR-2.

---

## Ownership (exclusive)

```text
frontend/components/writing/RightRail.tsx
frontend/components/writing/RailTabs.tsx
frontend/components/writing/WritingAiPanel.tsx (extend)
frontend/lib/aiActions.ts
frontend/lib/proposalQueue.ts
backend/app/graph/writer.py (Writing-panel action entry only)
backend/app/graph/orchestration/writer_prompt.py (action prompts)
backend/app/api/conversations.py or dedicated writing-actions endpoint
```

**Forbidden:** ContextBar/Inspector (EWO-001), MarkdownEditor (EWO-002),
SourcePicker (EWO-004), memory bundle modal (EWO-006).

---

## Scope

### In scope

1. **RightRail + RailTabs** — AI | Contesto | Fonte | Revisione; single slot; ⌘1–4
2. **≥4 AI actions** — e.g. Rewrite, Verify, Find sources, Expand (selection + chapter scoped)
3. **Streaming** — token append in panel; cancel button; `aria-live="polite"` on complete
4. **Applica flow** — Anteprima → Applica → proposal queue (not immediate persist)
5. **Selection-aware** — empty selection → chapter actions; selection → passage actions
6. **Disabled tooltips** when preconditions missing (spec §15.4)
7. **Context packet** passed to writer on every action (IR-3)

### Out of scope

- Session close bundle UI (PX2-EWO-006)
- Source peek reader content (PX2-EWO-004)
- Revision queue diff (PX2-EWO-007)
- `/ai` power mode changes

---

## Constraints

- ADR-0039 AI interaction model — lateral, not full-screen (IR-1)
- IR-2: no silent permanent writes
- IR-3: binding decisions in packet
- Writer graph existing topology — extend entry point, do not redesign M5 graph
- Italian action labels (IR-5)

---

## Acceptance Criteria

- [ ] At least 4 AI actions execute with streaming from Writing panel (AC-4)
- [ ] Applica creates proposal in queue — chapter content unchanged until approved (AC-5)
- [ ] Right rail tabs switch with ⌘1–4; default tab AI
- [ ] Selection changes action set; disabled actions show tooltip
- [ ] Cancel stops stream; partial result discarded
- [ ] Contesto tab renders ContextInspector from EWO-001
- [ ] Tests + `make ci` green

---

## Tests

- `WritingAiPanel.test.tsx` — streaming, Applica, disabled states
- `RailTabs.test.tsx` — keyboard shortcuts, aria tablist
- Backend: writer action invocation with context packet

---

## Regression

- `make ci`
- `/ai` power mode unchanged
- OR-7 proposal semantics preserved

---

## WO-TRACE

```text
PX2-EWO-001 + PX2-EWO-002 → PX2-EWO-003 → PX2-EWO-006, PX2-EWO-007
```
