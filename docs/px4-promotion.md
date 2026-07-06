# PX-4 — Knowledge Promotion

**Branch:** `main` · **Promotion commit:** `67acbc5e` (pre-tag baseline)  
**Product spec:** `docs/product/specs/thesisos-product-ux-v1.md` §5.5  
**ADR:** ADR-0037 (Knowledge Model), ADR-0042 (runtime boundary)  
**Program:** `.asep/programs/thesisos-product-v2.yaml`  
**Runtime contract:** `docs/product/runtime-integration-contract.md` v1.0

## Summary

PX-4 closes the **Knowledge** product milestone — concept-centric domain with
persisted CRUD, graph navigation, semantic search, and cross-module integration
with Sources, Writing, and Review workspaces.

Delivered across four engineering waves (0–3) plus conformance qualification
(PX4-EWO-011).

## Capability map (frozen baselines)

| Wave | EWO | Deliverable | Evidence |
|------|-----|-------------|----------|
| 0 | 001 | Product-runtime contract | `runtime-integration-contract.md` |
| 1 | 002 | Concept domain model | `models/knowledge.py` |
| 1 | 003 | Concept CRUD API | `api/knowledge.py` |
| 1 | 004 | Persistence + seed | migration `0006_knowledge_concepts` |
| 2 | 005 | DB-backed graph | `services/knowledge/graph.py` |
| 2 | 006 | Explorer search UI | `KnowledgeExplorerSearch` |
| 2 | 007 | Knowledge search API | `services/knowledge_search.py` |
| 3 | 008 | Sources ↔ Knowledge | `api/sources.py` detail + links |
| 3 | 009 | Writing context bridge | `context/knowledge_bridge.py` |
| 3 | 010 | Review knowledge panel | `ReviewKnowledgePanel` |

## Qualification

| Gate | Report / certificate | Verdict |
|------|---------------------|---------|
| Integration B | `PX4-INTEGRATION-B.md` | PASS |
| Integration C | `PX4-INTEGRATION-C.md` | PASS |
| Integration D | `PX4-INTEGRATION-D.md` | PASS |
| Conformance E2E | `PX4-EWO-011-conformance.md` | PASS |
| Promotion | `PX4-PROMOTION-20260706.yaml` | PROMOTED |

## Promotion gates

```yaml
phase_0_contract: green
wave_1_foundation: green
wave_2_graph_explorer: green
wave_3_integration: green
px4_ewo_011_conformance: green
adr_0037_c1_c2_c3: green
make_ci: green
unit_m4_recovery: green
px2_px3_regression: green
scope_creep: false
documentation: complete
px4_complete_tag: px4-complete
```

## Tag

- `px4-complete` on promotion commit (Architect-authorized 2026-07-06)

## Out of scope (post-promotion)

- PX-5 Research canvas / exploratory graph
- PX-6 Polish
- MB2 runtime internals
- SoR / Constitution amendments
