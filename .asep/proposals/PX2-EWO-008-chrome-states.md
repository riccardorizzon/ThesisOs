# Engineering WorkOrder Proposal — PX2-EWO-008

> **Status:** ⏳ **PROPOSED** — dispatch blocked until amendment ratified.
>
> Program: `.asep/programs/thesisos-product-v2.yaml`  
> Capability: `px2-ewo-008-chrome-states`  
> Spec: `docs/product/specs/px2-research-workspace-experience.md` §16–21  
> UI: `design-system/thesisos/px2-research-workspace-ui-spec.md` §3–4, §10–11

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX2-EWO-008 |
| **Sub-agent** | H (integration) |
| **Type** | **EWO** — Release |
| **EWO category** | **Release** |
| **Capability** | `px2-ewo-008-chrome-states` |
| **User capability** | All PX-2.1…2.5 (cross-cutting) |
| **Milestone** | PX-2 |
| **Layer** | Business |
| **Wave** | px2-parallel/wave_d |
| **Depends on** | PX2-EWO-001…007 |

---

## Objective

Integrate **Command palette** (⌘K), **keyboard shortcuts**, **empty/loading/error states**,
**responsive breakpoints**, **contextual onboarding**, and **AppShell chrome** updates —
closing PX-2 integration before QWO-PX2-001.

---

## Ownership (exclusive)

```text
frontend/components/chrome/CommandPalette.tsx
frontend/components/onboarding/CoachMark.tsx
frontend/components/AppShell.tsx (session chip slot, ⌘K affordance, nav badges)
frontend/hooks/useKeyboardShortcuts.ts
frontend/hooks/useReducedMotion.ts
frontend/styles/tokens.css (PX-2 layout tokens)
frontend/tailwind.config.ts (width extensions)
frontend/components/OfflineBanner.tsx (or chrome/)
```

**Forbidden:** Feature logic inside writing/sources/review modules — wire only.

---

## Scope

### In scope

1. **CommandPalette** — ⌘K / ⌘⇧P; discoverability list of all shortcuts (spec §16)
2. **Keyboard map** — ⌘\, ⌘⇧\, ⌘⇧C, ⌘⇧R, G→W/S/H, ⌘↑/↓, Esc behaviors
3. **Empty states** — all surfaces per spec §17
4. **Loading states** — skeleton patterns per spec §18
5. **Error states** — Italian messages per spec §19; OfflineBanner
6. **CoachMark** — contextual onboarding max 3 steps; dismiss forever
7. **Responsive** — breakpoints 1280/1024/768; read-only banner <768px
8. **Nav badges** — Writing status dot, Review pending count
9. **Token additions** — `--outline-width`, `--rail-width`, etc. per UI spec §1.1
10. **Integration smoke** — all workspace routes wired; no orphan stubs

### Out of scope

- New feature behavior (owned by EWO-001…007)
- Marketing tour
- Mobile writing support

---

## Constraints

- IR-5: Italian operator / English nav
- `prefers-reduced-motion` honored (UI spec §3)
- Keyboard shortcuts do not override browser defaults without focused workspace
- No layout shift on hover (UI spec §3)

---

## Acceptance Criteria

- [ ] ⌘K opens command palette with full shortcut discoverability
- [ ] All spec §16 shortcuts functional in Writing workspace
- [ ] Empty/loading/error states match spec §17–19 copy tables
- [ ] Coach marks on Continua, three panels, ContextBar (skippable)
- [ ] Responsive behavior at 1280/1024/768 breakpoints
- [ ] Read-only banner below 768px
- [ ] PX-2 layout tokens in tokens.css + Tailwind
- [ ] `make ci` green; all PX-2 EWO integration smoke passes

---

## Tests

- `CommandPalette.test.tsx` — open, search, execute actions
- `useKeyboardShortcuts.test.ts` — chord sequences
- `CoachMark.test.tsx` — dismiss, max steps
- AppShell integration test — badges, ⌘K affordance

---

## Regression

- `make ci`
- PX-1 AppShell navigation unchanged
- OR-1…OR-7 regression green

---

## WO-TRACE

```text
PX2-EWO-001…007 → PX2-EWO-008 → QWO-PX2-001
```
