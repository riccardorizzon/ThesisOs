# Architect Authorization — PX-5 Research

Program: thesisos-product-v2  
Milestone: PX-5 — Research  
Role: engineering  
Status: **AUTHORIZED**  
Authorized EWO: **PX5-EWO-001**  
Pre-flight: **PASS**  
Operator command: `ASEP: AUTHORIZE PX-5 Research`  
Timestamp: 2026-07-06

---

## Pre-flight summary

| Check | Result |
|-------|--------|
| Program graph | ✓ `.asep/programs/thesisos-product-v2.yaml` |
| PX-3 conformance complete | ✓ Assessment PASS + Architect ratification + graph sync |
| PX-3 completion certificate | ✓ `.asep/certificates/PX3-CONFORMANCE-COMPLETE-20260706.yaml` |
| PX-4 promoted | ✓ `px4-complete` @ `d5206a0f` |
| PX-4 promotion certificate | ✓ `.asep/certificates/PX4-PROMOTION-20260706.yaml` |
| Product Constitution | ✓ frozen |
| Runtime integration contract | ✓ `docs/product/runtime-integration-contract.md` v1.0 |
| INV-KM-5 prerequisite | ✓ Concept model shipped (PX-4) |
| Wave A backlog | ✓ `.asep/reports/PX5-WAVE-A-BACKLOG.md` |
| Proposal filed | ✓ `.asep/proposals/PX5-EWO-001-research-experience-spec.md` |
| `make ci` | ✓ green @ `d5206a0f` |
| Repository | ✓ clean (governance sync in progress) |
| First executable EWO | ✓ PX5-EWO-001 (no deps) |

---

## Scope boundary

This authorization covers **PX-5 milestone entry** and **Wave A spec foundation**
(PX5-EWO-001). It does **not** authorize:

- Research canvas implementation before ratified product spec
- MB2 runtime / SoR / Constitution modifications
- px-exec Runtime Engineering
- PX-6 Polish

---

## Authorized EWO

| Field | Value |
|-------|-------|
| **Id** | PX5-EWO-001 |
| **Title** | Research Experience Spec + UX foundation |
| **Category** | Alignment |
| **Layer** | Business |
| **Proposal** | `.asep/proposals/PX5-EWO-001-research-experience-spec.md` |

### Deliverables (in scope)

- `docs/product/specs/px5-research-experience-v1.md` (normative product spec)
- `design-system/thesisos/px5-research-experience-ui-spec.md` (UI spec draft)
- `.asep/reports/PX5-EWO-001-research-experience-spec.md` (PASS report)

### Boundary constraints

| Surface | PX-3 | PX-4 | PX-5 |
|---------|------|------|------|
| `/knowledge/graph` | Navigation graph (15-node default) | Concept model + Explain | Must not expand into canvas |
| `/research` | Guided exploration (PX-3 §16) | Stub cross-links | **Spatial research canvas** (this milestone) |

Preserve **INV-KM-5**: Research graph UX must build on PX-4 concept model.

---

## Explicitly NOT authorized

| Scope | Status |
|-------|--------|
| PX-6 Polish | **NOT authorized** |
| MB2 runtime internals | **NOT authorized** |
| SoR / Constitution modifications | **NOT authorized** |
| px-exec / Runtime Engineering | **NOT authorized** |
| Implementation EWOs (canvas, discovery API) | **NOT authorized** until spec PASS |

---

## WO-TRACE

```text
PX-3 COMPLETE (conformance) → PX-4 PROMOTED (px4-complete)
  → Program graph sync → AUTHORIZE PX-5
  → PX5-EWO-001 Research Experience Spec (authorized)
  → Implementation waves (future — requires spec PASS + separate wave authorization)
```

---

## Recommended next action

Execute **PX5-EWO-001**: draft `px5-research-experience-v1.md` from
`thesisos-product-ux-v1.md` §5.2 + ADR-0037 Research domain, file UI spec draft,
obtain Architect ratification, then spawn Wave A implementation EWOs.
