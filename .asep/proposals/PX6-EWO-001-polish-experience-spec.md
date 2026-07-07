# Engineering WorkOrder Proposal — PX6-EWO-001

> **Status:** **PROPOSED** — pending `ASEP: develop PX6-EWO-001`

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  category: A
  hypothesis_id: n/a
  success_metric: "PX-6 product spec ratified with W-06 mitigation architecture documented"
  exit_id: n/a
  program_mode: product
```

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX6-EWO-001 |
| **Title** | Polish Experience Spec + UX foundation |
| **Milestone** | PX-6 |
| **Layer** | Business |
| **Category** | Alignment |
| **Wave** | A |

## Objective

Ratify the **PX-6 Polish** product specification and UI spec draft, defining the
terminal v2.0 milestone scope: W-06 citation validator (product mitigation layer),
bibliography export, multi-project switch, outline reorder, settings depth, typography,
and performance polish — with explicit boundaries vs PX-2…PX-5.

## Deliverables

- `docs/product/specs/px6-polish-experience-v1.md` — normative product spec
- `design-system/thesisos/px6-polish-experience-ui-spec.md` — UI spec draft
- `.asep/reports/PX6-EWO-001-polish-experience-spec.md` — PASS report

## Acceptance

- [ ] Product spec covers capabilities PX-6.1…PX-6.7 per `.asep/reports/PX6-BACKLOG.md`
- [ ] W-06 mitigation architecture documented (product validation — not OR-6 re-proof)
- [ ] Boundary table: PX-2 cite flow vs PX-6 validator vs thesis-agent enforcement
- [ ] Export formats and multi-project isolation rules specified
- [ ] QWO-PX6-001 draft acceptance criteria (AC-1…AC-11) included in spec §16
- [ ] UI spec defines validator inline states, export dialog, project switcher, settings sections
- [ ] No implementation code in this EWO (spec-only)

## Dependencies

- PX-5 promoted (`px5-complete`)
- PX-6 milestone authorized — `.asep/reports/PX6-AUTHORIZATION-20260707.md`
- Backlog design — `.asep/reports/PX6-BACKLOG.md`

## Forbidden

- Modifying SoR, Runtime Constitution, or `builder_engine/` MB2 surfaces
- Claiming deterministic author-date LLM output (W-06 remains Platform Limitation with mitigation)
- Implementing validator, export, or multi-project code before spec ratification
- Separate Reviewer/Planner agent topology without Product ADR supersession

## Downstream

On PASS → spawn Wave B proposals (PX6-EWO-002…004) and request Wave B authorization.
