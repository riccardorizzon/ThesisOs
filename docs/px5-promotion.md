# PX-5 — Research Promotion

**Branch:** `main` · **Baseline HEAD:** `b6c04da9` (Wave E delta on working tree)  
**Product spec:** `docs/product/specs/px5-research-experience-v1.md`  
**UI spec:** `design-system/thesisos/px5-research-experience-ui-spec.md`  
**Program:** `.asep/programs/thesisos-product-v2.yaml`  
**Qualification:** `QWO-PX5-001` @ `.asep/reports/QWO-PX5-001.md`

## Summary

PX-5 closes the **Research** product milestone — spatial discovery canvas with
discovery lenses, serendipity paths, satellite nodes, session basket with Writing
handoff, saved views, and performance affordances (minimap, cluster, hard-limit modal).

Delivered across five engineering waves (A–E) plus Integration D/E gates.

## Capability map (frozen baselines)

| Wave | EWO | Deliverable | Evidence |
|------|-----|-------------|----------|
| A | 001 | Research experience spec | `px5-research-experience-v1.md` |
| B | 002 | Hub + route scaffolding | `/research`, `/research/canvas` |
| C | 003 | Canvas viewport + concept layer | `ResearchCanvasViewport` |
| D | 004…007 | Shell, lenses, inspector, serendipity | `PX5-INTEGRATION-D.md` |
| E | 008…011 | Satellites, basket, views, minimap | `PX5-INTEGRATION-E.md` |

## Qualification

| Gate | Report | Verdict |
|------|--------|---------|
| Integration D | `PX5-INTEGRATION-D.md` | PASS |
| Integration E | `PX5-INTEGRATION-E.md` | PASS |
| QWO-PX5-001 | `QWO-PX5-001.md` | PASS |
| Promotion | `PX5-PROMOTION-20260707.yaml` | PROMOTED |

## Promotion gates

```yaml
wave_a_spec: green
wave_b_hub: green
wave_c_viewport: green
wave_d_discovery: green
wave_e_satellites_polish: green
px5_integration_d: green
px5_integration_e: green
qwo_px5_001: green
make_ci: green
px2_px3_px4_regression: green
scope_creep: false
documentation: complete
px5_complete_tag: px5-complete
```

## Tag

- `px5-complete` — apply on promotion commit (Architect-authorized 2026-07-07)

## Out of scope (post-promotion)

- PX-6 Polish (citation validator, export, multi-project)
- Full guided trail implementation (PX-3 scope)
- MB2 runtime internals
- SoR / Constitution amendments
