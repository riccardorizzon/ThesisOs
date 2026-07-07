# Engineering WorkOrder Proposal — PX5-EWO-004

> **Status:** **AUTHORIZED** — `.asep/reports/PX5-AUTHORIZATION-WAVE-D-20260707.md`

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  category: A
  hypothesis_id: n/a
  success_metric: "Canvas shell with multi-select per px5-research-experience-v1.md §5.4 and UI spec §4.1"
  exit_id: n/a
  program_mode: product
```

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX5-EWO-004 |
| **Title** | Canvas shell + selection model |
| **Milestone** | PX-5 |
| **Wave** | D |
| **Layer** | Business (Product Plane) |

## Objective

Replace the Wave C single-column page with the **three-region canvas shell** and
upgrade selection to product §5.4 multi-select gestures.

## Deliverables

- Refactor `ResearchCanvasPage` → shell layout (lens rail slot | canvas | inspector slot)
- Header bar: back, lens dropdown (disabled until EWO-006), filters popover stub, basket badge (count 0, disabled)
- Lift viewport transform + selection state to page/shell context
- Multi-select: `⌘`+click toggle, Shift+drag marquee, Esc clear
- Action bar footer: selection count; handoff buttons disabled until Wave E
- Responsive breakpoints per UI spec §14 (desktop-required message `<1024px`)
- `ResearchCanvasShell.test.tsx` (or equivalent shell tests)
- `.asep/reports/PX5-EWO-004-canvas-shell-selection.md`

## Acceptance

- [ ] Shell matches UI spec §4.1 region widths (240px lens, flex canvas, 320px inspector slot)
- [ ] Multi-select updates selection set; single click replaces when no modifier
- [ ] Esc clears selection
- [ ] Viewport pan/zoom/selection coexist — node click does not trigger pan
- [ ] `<1024px` shows desktop-required message (RR-8)
- [ ] `make ci` green; Wave C viewport regression preserved

## Dependencies

- PX5-EWO-003 PASS (canvas viewport + node layer)

## Forbidden

- Lens filter logic, inspector content, serendipity strip
- Basket persistence, saved views
- SoR / Constitution / `builder_engine/` changes
