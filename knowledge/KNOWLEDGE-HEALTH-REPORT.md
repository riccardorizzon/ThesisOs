# Knowledge Health Report v2

> Audit after **M2 Phase 5 Knowledge Freeze** (2026-06-24). Supersedes v1 sections that are stale; full v1 history preserved below where still valid.

## Executive summary

**Health: Good — materially improved since v1.**

M2 now has a **frozen spec**, three new ADRs, a working vertical slice (DB → Service → API → Admin UI), and an updated `knowledge/` mirror. A new agent can onboard from `current-state.md` + `project-memory.md` + `architecture/memory.md` without reading the full repo.

**Remaining gap before M2 promotion:** Phase 6 graph integration + Critic/QA sign-off. **Remaining gap before M3:** frozen M3 design spec.

---

## v2 deltas (what changed since v1)

| Area | v1 | v2 |
|------|----|----|
| M1 status | validated, not tagged | ✅ `m1-complete` on `main` |
| M2 spec | missing | ✅ frozen (`2026-06-24-thesisos-m2-memory-system-design.md`) |
| M2 code | not started | ✅ Phases 1–4 on `m2-memory-system` |
| ADR count | 14 | 18 (+0015, 0017, 0018) |
| Domain tables | 14 | 15 (+`memory_versions`) |
| Frontend tests | none | ✅ Vitest 15 (memory admin) |
| Backend tests | 23 pass | 35 pass (+ memory) |
| `architecture/memory.md` | "not yet built" | ✅ reflects implementation |
| `docs/m2-promotion.md` | missing | ✅ created (partial gate) |
| pgvector on memory | "deferred M2/M4" | **M2 forbids**; M4 only (ADR-0018) |

---

## Coverage confidence (v2)

| Knowledge area | Confidence | Notes |
|----------------|------------|-------|
| M0/M1 | High | promoted, gated |
| M2 memory (service/API/UI) | High | code + spec + architecture/memory.md aligned |
| M2 graph injection | Medium | designed in spec; not implemented |
| M3–M18 | Low | specs not frozen |
| Agent onboarding | **High** | current-state + project-memory sufficient for M2 handoff |

---

## Critic findings (documentation pass — Phase 5)

| ID | Finding | Severity | Status |
|----|---------|----------|--------|
| K1 | `next-actions.md` T021 conflated `memory_context_node` with `memory_ops` agent node — different concerns | Med | Documented: Phase 6 = context loader; M5 = ops executor |
| K2 | `milestones.md` still said M1 untagged | Med | ✅ fixed in v2 |
| K3 | `architecture/memory.md` said "not yet built" | Med | ✅ fixed |
| K4 | T028 "embeddings on memories" contradicted ADR-0018 | High | **Rejected** — embeddings on memory deferred to M4; removed from M2 path |
| K5 | No promotion doc for M2 | Med | ✅ `docs/m2-promotion.md` |
| K6 | Knowledge not updated at phase boundaries | Med | ✅ Phase 5 rule now applied |

No unresolved documentation contradictions for M2 Phases 1–4.

---

## Architecture risks (updated)

1. **R1 (HIGH) — pgvector index** — unchanged; owner **M4** (Q1). M2 correctly avoids early embeddings.
2. **R7 (NEW, MED) — Graph injection before UI validation** — mitigated by Service→API→UI sequencing; Phase 6 proceeds after Admin UI.
3. **R8 (NEW, LOW) — `memory_ops` vs `memory_context_node` naming** — two different nodes; document in M5 spec to avoid duplicate "memory node".
4. **R4 (MED) — in-process conversation lock** — unchanged; single-instance assumption.

---

## Recommendations (v2 prioritized)

1. **Execute M2 Phase 6** with Critic + QA gates before tag.
2. **Architect: freeze M3 spec** before any ingestion code (Docling, chunks, GCS — no embeddings).
3. **Keep knowledge updated** at every phase boundary (now a promotion habit).
4. **Wire `MemoryUpdated`** during or immediately after Phase 6.
5. **Refresh `knowledge/contracts/api-contracts.md`** when M2 merges ( `/memory` no longer 501).
6. **Add M2 snapshot** to `knowledge/snapshots/` at tag time (mirror `m1-complete.json` pattern).

---

## v1 report (2026-06-24 initial build)

The original Knowledge Health Report follows. Items marked fixed above may still appear in v1 prose — prefer v2 deltas when they conflict.

# Knowledge Health Report (v1)

> Audit of the ThesisOS knowledge base vs the repository, produced while building `knowledge/`. Scope: what's documented, what's missing, contradictions found (and how resolved here), knowledge gaps, architecture risks, and recommendations. Sources cited inline; nothing invented.

## Summary verdict

**Healthy and unusually disciplined for its size.** The repo is Contract-First with
frozen specs, 14 ADRs, evidence-backed promotion gates, and a clean seam-first M1.
Documentation density is high for **M0/M1** and **thin for M2–M18** (by design —
specs are frozen per milestone). The biggest *operational* gap is that **M1 is
validated but not yet deployed/tagged**, and the biggest *durability* gap is the
absence of frozen specs for future milestones.

*(v2 note: M1 now tagged; M2 spec exists; M2 Ph1–4 built.)*

---

## 1. Missing documentation

| Gap | Impact | Where it should live |
|-----|--------|----------------------|
| **No frozen design specs for M2–M18** | Medium — future agents must derive scope from contracts | `docs/superpowers/specs/` (one per milestone, before impl) |
| **No detailed scope for M13 (Research), M14 (NotebookLM-like), M17 (Voice)** | Low now, Medium later | roadmap names only; need specs |
| **No `docs/m2..m18-promotion.md`** | Expected (not started) | created per milestone |
| **Frontend has no test runner / tests** | Medium — UI regressions slip | add Vitest + SSE-parser test (T016) |
| **No end-to-end test for `ConversationService.stream_turn`** | Medium — core path only smoke-tested | T014/T015 |
| **`infra/scripts/` is empty** | Low | populate or remove |
| **No explicit auth/exposure policy doc** | Low (single-user) | IAP guidance only in `docs/m0-runbook.md` §3; capture in a security note |
| **No contracts changelog** | Low | a `contracts/CHANGELOG.md` would make additive evolution auditable |

*(v2: M2 spec ✅; m2-promotion ✅; frontend vitest ✅ for memory; M2–M17 specs still missing.)*

---

## Maintenance rule

Regenerate the **v2 summary section** at each promotion gate. The KB mirrors the repo — when in doubt, read cited sources (`docs/m2-promotion.md`, code, tests).
