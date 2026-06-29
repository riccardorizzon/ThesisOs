# Architecture Invariants

> **Living index** of architectural invariants across the Product Plane.
> Baseline: **`m6-main`** @ `79fb52a` (integrated on `main`, 2026-06-29).
> Qualified branch baseline: **`m6-complete`** @ same SHA (immutable; never moved).
>
> Each invariant cites its authority. New milestones append entries here; they do
> not rewrite prior ones without an ADR.

---

## Layering & composition

### Invariant 1 — GraphState frozen

`GraphState` field set is **frozen** (ADR-0007). No add/remove/retype without a
new ADR. M0–M6 added nodes and routes without changing the shape.

**Authority:** ADR-0007, Constitution C5, `knowledge/contracts/graphstate.md`

### Invariant 2 — RunContext never in GraphState

Execution metadata (`conversation_id`, `trace_id`, `agent_run_id`, …) flows via
LangGraph `config.configurable.run_context`, never as a GraphState field.

**Authority:** ADR-0014, Constitution C5, GraphState invariant 3

### Invariant 3 — Layer dependencies flow downward

```text
Business → Runtime → Infrastructure
```

Inverse dependencies are forbidden. Every PR touching `backend/app/` declares
its layer (Business | Runtime | Infrastructure).

**Authority:** Constitution C1, ADR-0030 §1

### Invariant 4 — Composition root binds layers

Only `build_graph()`, `ConversationService`, and test fixtures wire Business,
Runtime, and Infrastructure together. Business nodes receive injected ports/hooks.

**Authority:** Constitution C2, ADR-0030 R2

### Invariant 5 — Business nodes pure

Business logic does not import database, telemetry, logging, event bus, or
LangGraph internals. It depends on injected ports and domain types only.

**Authority:** Constitution C3, ADR-0030 R1/R3

---

## Capabilities & extension

### Invariant 6 — Capability over node

Agents are **capabilities** (ports) swappable at the composition root without
topology change. Example: `WriterCapability.write_grounded(brief) → DraftResult`;
`LLMWriter` is today's default, not the only implementation.

**Authority:** Constitution C8, ADR-0031, `docs/runtime-contract.md` §5

### Invariant 7 — Extension through documented points

New agents, subscribers, and runtime components attach only via documented
extension points (`docs/runtime-contract.md`). No direct cross-layer imports.

**Authority:** Constitution C8, ADR-0030 R7

### Invariant 8 — M4+ compatibility unless ADR authorizes

Changes must not alter validated behavior of frozen milestones unless an ADR
explicitly authorizes the change (generalizes beyond M4 to any qualified baseline).

**Authority:** Constitution C6, `docs/m4-freeze.md`

---

## Writer & drafting (M6)

### Invariant 9 — DraftResult is pure

`DraftResult { draft, citations, metadata, reasoning?, metrics }` is produced by
the writer capability without importing `app.db`, `app.runtime`, `app.services`,
REST, or persistence. The node adapter maps **only** `draft` and `citations` to
GraphState; richer fields ride the stream / Event Bus.

**Authority:** ADR-0031, `contracts/agents/writer.json`

### Invariant 10 — Citation discipline

Every `CitationRef.source_id` in writer output must be a subset of
`retrieved_context` chunk source ids. No invented sources.

**Authority:** ADR-0031, M6 qualification (`test_m6_writing_eval.py`)

### Invariant 11 — Grounding wire only

Chunk text enters the LLM only via `retrieved_context` → prompt composition —
never persisted in DB messages. Client receives reference metadata via SSE
`sources` events.

**Authority:** ADR-0024, `docs/m4-freeze.md`

---

## Persistence

### Invariant 12 — Single writer per aggregate

`ChapterService` is the **sole writer** for `chapters` and `chapter_versions`.
Graph nodes and HTTP handlers never write chapter rows directly.

**Authority:** ADR-0032, ADR-0015 pattern, ADR-0030 R4

### Invariant 13 — Chapter versioning is append-only

Chapter history is a change stream: `change_kind ∈ {WRITE, EDIT, PROMOTE, MERGE,
RESTORE}`. Optimistic locking via `expected_version` → HTTP 409 on conflict.

**Authority:** ADR-0033

### Invariant 14 — Drafts do not auto-persist from graph

The writer produces ephemeral `DraftResult`. Persistence to chapters is explicit
via `ChapterService` / `/chapters` (user or API action), not from graph nodes.

**Authority:** ADR-0031, ADR-0032

---

## Runtime events & observability (M5)

### Invariant 15 — Canonical events only

The Runtime emits a closed vocabulary of canonical events. Subscribers are
replaceable; zero subscribers is valid and silent.

**Authority:** Constitution C4, ADR-0030 R6/R8

### Invariant 16 — Business never emits events

Event emission happens at the composition root and Runtime instrumentation
wrappers, never inside Business node bodies.

**Authority:** ADR-0030 R8

### Invariant 17 — Subscriber failure is non-blocking

A failing subscriber must not abort a turn. The Event Bus fan-out is best-effort.

**Authority:** ADR-0030 R6, Constitution C4

---

## External seams

### Invariant 18 — `/chat` SSE seam frozen

`POST /chat` → `ConversationService` → LangGraph `astream` → SSE is the M1 seam.
Later milestones extend the graph; they do not rewrite this path.

**Authority:** ADR-0011, M1 spec §1, M5/M6 qualification gates

### Invariant 19 — Contract-first public surfaces

Agent contracts (`contracts/agents/*.json`), OpenAPI paths, event catalog, and
`GraphState` are versioned. Incompatible changes require an ADR.

**Authority:** Constitution C5, ADR-0001

---

## Review discipline

### Invariant 20 — Review order

Every review proceeds: Constitution → Layer → Contracts → Events → Feature →
Performance → Code.

**Authority:** Constitution C7, `docs/architecture-decision-checklist.md`

---

## Future (reserved — not yet enforced)

These slots are reserved for upcoming milestones. Do not implement without spec
+ ADR.

| Slot | Planned invariant | Milestone |
|------|-------------------|-----------|
| 21 | Grounding evidence originates only from `retrieved_context` | M7 Grounding Engine |
| 22 | CSL-JSON sources are canonical; formatters are pure transforms | M7 |
| 23 | Critic reads draft + grounding; does not mutate GraphState shape | M9 |

---

## Amendment rule

Add a numbered invariant when a milestone introduces a new rule. Change an existing
invariant only via ADR that names the invariant and updates this document.
