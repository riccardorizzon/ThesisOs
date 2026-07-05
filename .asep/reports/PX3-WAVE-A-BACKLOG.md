# PX-3 Wave A — Backlog Definition

> **Authority:** Architect (product architecture)  
> **Date:** 2026-07-05  
> **Program:** `.asep/programs/thesisos-product-v2.yaml`  
> **Milestone:** PX-3 Knowledge Experience (Conformance Program)  
> **Scope:** Wave A only — subsequent waves not planned here

---

## Functional objective (PX-3)

Deliver the **Knowledge Experience** milestone: activate the Knowledge module and enrich
Sources as knowledge objects, under the frozen MB2 SoR.

**Product thesis** (`px3-knowledge-experience-v2.md` §1):

```text
PX-2 = Workspace  →  Where do I work?
PX-3 = Knowledge  →  What does my research know?
```

Wave A establishes the **Knowledge Object substrate** and delivers the first two
operator-visible surfaces — enriched Sources list and Knowledge Explorer — without
committing to Explain Page, Graph, Reader enrichment, or Research workflow (later waves).

---

## Authoritative sources (not agent-invented)

| Artifact | Role |
|----------|------|
| `docs/product/specs/px3-knowledge-experience-v2.md` | Product spec §3–§8, §12 |
| `design-system/thesisos/px3-knowledge-experience-ui-spec.md` | UI spec (FROZEN) §5.1, §5.4 |
| `design-system/thesisos/product-patterns.md` | PP-09 entity envelope |
| `decisions/ADR-0036-information-architecture.md` | Routes, `/documents/*` → `/sources/*` |
| `decisions/ADR-0037-knowledge-model.md` | Concepts canonical |
| `.asep/governance/sor-compatibility-policy.md` | Conformance policy |

**Deferred to later waves (not Wave A):** Explain Page (§9), Knowledge Graph (§10),
Source reader enrichment (§5.5), annotations (§7), citations (§11), authors (§9),
Research workflow (§16), full source import/PDF parse.

---

## Wave A DAG

```text
PX3-EWO-001  Knowledge Object Foundation
      │
      ├──────────────────┐
      ▼                  ▼
PX3-EWO-002          PX3-EWO-003
Sources Enrichment   Knowledge Explorer
      │                  │
      └────────┬─────────┘
               ▼
      PX3-EWO-004  Wave A Integration
```

| EWO | Title | User capability | Parallel after |
|-----|-------|-----------------|----------------|
| **PX3-EWO-001** | Knowledge Object Foundation | Substrate (PX-3.1…3.10 enabler) | — (first executable) |
| **PX3-EWO-002** | Sources Module Enrichment | PX-3.1 (partial), PX-3.5 (list) | 001 |
| **PX3-EWO-003** | Knowledge Explorer | PX-3.2 | 001 |
| **PX3-EWO-004** | Wave A Integration | Cross-module wiring | 002 + 003 |

**First executable EWO:** `PX3-EWO-001` (no dependencies).

---

## Execution model

Parallel program: `.asep/programs/px3-parallel.yaml`

```text
AUTHORIZE PX-3
      ↓
Pre-flight PASS
      ↓
PX3-EWO-001 (sequential — foundation)
      ↓
PX3-EWO-002 ∥ PX3-EWO-003 (parallel — disjoint ownership)
      ↓
PX3-EWO-004 (integration — supervisor)
      ↓
(Wave B+ — not defined)
```

Conformance: product code only; deviations → `.asep/reports/PX3-CONFORMANCE-LOG.md`.

---

## WO-TRACE

```text
PX-2 FROZEN → MB2 SoR FREEZE → Wave A backlog registered
  → AUTHORIZE PX-3 → PX3-EWO-001 → … → PX3-EWO-004
```
