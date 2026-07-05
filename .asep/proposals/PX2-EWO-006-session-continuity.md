# Engineering WorkOrder Proposal — PX2-EWO-006

> **Status:** ⏳ **PROPOSED** — dispatch blocked until amendment ratified.
>
> Program: `.asep/programs/thesisos-product-v2.yaml`  
> Capability: `px2-ewo-006-session-continuity`  
> Spec: `docs/product/specs/px2-research-workspace-experience.md` §7, §14  
> UI: `design-system/thesisos/px2-research-workspace-ui-spec.md` §4.1, §7

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX2-EWO-006 |
| **Sub-agent** | F |
| **Type** | **EWO** — Infrastructure |
| **EWO category** | **Infrastructure** |
| **Capability** | `px2-ewo-006-session-continuity` |
| **User capability** | **PX-2.5** Session Continuity |
| **Milestone** | PX-2 |
| **Layer** | Business + Infrastructure |
| **Wave** | px2-parallel/wave_b |
| **Depends on** | PX2-EWO-002, PX2-EWO-003 |

---

## Objective

Implement **session persistence**, **Continua deep links**, **URL restorable state**,
and **atomic session close** with proposal bundle — operator resumes work across
sessions without rebuilding context.

---

## Ownership (exclusive)

```text
frontend/components/chrome/SessionChip.tsx
frontend/components/memory/ProposalBundleModal.tsx
frontend/components/HomeView.tsx (Continua + activity — extend)
frontend/lib/sessionState.ts
frontend/lib/continuaLink.ts
frontend/lib/projectContext.ts (session fields)
backend/app/services/memory/service.py (session bundle — read/approve path)
backend/app/schemas/memory.py (bundle schema if needed)
```

**Forbidden:** MarkdownEditor, SourcePicker, ReviewCompare, graph topology.

---

## Scope

### In scope

1. **SessionChip** — duration + pending proposal count; click → Chiudi sessione
2. **URL state** — `/writing/cap-03?section=3.2&source=src-benjamin&panel=fonte`
3. **Continua** — Home CTA restores chapter, section, scroll, rail tab, peeked source
4. **ProposalBundleModal** — atomic approve/reject all proposals (OR-7)
5. **Activity feed** — proposal types per UI spec §7
6. **localStorage/session persistence** — panel collapse, last route, scroll position
7. **Nav badge** — Home proposal count pill

### Out of scope

- Multi-project switcher (PX-6)
- Tier names Permanent/Ephemeral in UI (OR-7 — never shown)
- Backend memory tier redesign

---

## Constraints

- OR-7: session close atomic — approve/reject all together
- IR-2: proposals only until bundle approved
- Continua must reach productive writing in 90s (spec success metric — verified in QWO)
- ADR-0040 progress updates on chapter status change (AC-12 hook)

---

## Acceptance Criteria

- [ ] Continua restores chapter, section anchor, and panel tab (AC-9)
- [ ] Session close presents atomic proposal bundle (AC-10)
- [ ] URL query params restore writing workspace state
- [ ] SessionChip shows duration and pending count
- [ ] Home progress ring updates on chapter status change (AC-12)
- [ ] Activity feed shows proposal/decision/source event types
- [ ] Tests + `make ci` green

---

## Tests

- `sessionState.test.ts` — serialize/deserialize URL state
- `continuaLink.test.ts` — deep link generation
- `ProposalBundleModal.test.tsx` — atomic approve/reject
- `HomeView.test.tsx` — Continua link targets

---

## Regression

- `make ci`
- OR-7 memory protocol unchanged
- PX-1 Home layout preserved

---

## WO-TRACE

```text
PX2-EWO-002 + PX2-EWO-003 → PX2-EWO-006 → QWO-PX2-001
```
