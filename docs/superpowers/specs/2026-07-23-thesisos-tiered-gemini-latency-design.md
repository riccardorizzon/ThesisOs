# ThesisOS — Tiered Gemini and Chat Latency Design

- **Date:** 2026-07-23
- **Status:** Design approved by Architect; written specification awaiting review
- **Scope:** Product-plane LangGraph model routing and chat response latency
- **Decision:** GA-only Gemini tiers; preserve the complete LangGraph

---

## 1. Context and Goal

The deployed Companion is correct but slow. A measured continuation turn took 23.5 seconds
before the first visible token:

| Stage | Duration |
|---|---:|
| Supervisor | 1.368 s |
| Planner | 5.083 s |
| Router | 3.176 s |
| Workspace + memory context | 0.043 s |
| Conversation generation | 13.551 s |

The Cloudflare tunnel added only about 18 ms. The delay comes from four sequential
`gemini-2.5-pro` calls and from buffering the final generation before emitting it.

The goal is to reduce time-to-first-token without weakening thesis quality, citation
enforcement, project isolation, persistence, or the Grounded and Writer branches.

## 2. Model Policy

Use stable, generally available models only:

| Responsibility | Model | Reason |
|---|---|---|
| Supervisor, Planner, Router | `gemini-3.5-flash-lite` | Low-latency structured decisions |
| Companion, Conversation, Writer | `gemini-3.6-flash` | Strong current GA model for knowledge work and agentic execution |

Both models are verified against the configured Google Cloud project. They require the
Vertex `global` location; the current `europe-west1` endpoint returns `404`.

Configuration gains a distinct orchestration model while retaining `gemini_model` as the
response-model setting:

```text
VERTEX_LOCATION=global
GEMINI_MODEL=gemini-3.6-flash
GEMINI_ORCHESTRATION_MODEL=gemini-3.5-flash-lite
```

No preview model and no multi-provider fallback are introduced.

## 3. Architecture

`build_graph` accepts the response client as it does today and an optional orchestration
client:

```text
build_graph(response_llm, orchestration_llm=None, ...)
```

When `orchestration_llm` is omitted it falls back to `response_llm`, preserving all
existing tests and call sites. The production composition root supplies both:

```text
Supervisor ─┐
Planner ────┼─ gemini-3.5-flash-lite
Router ─────┘

Conversation ─┐
Writer ───────┴─ gemini-3.6-flash
```

Retriever, workspace context, memory, checkpointing, runtime events and SSE contracts do
not change.

## 4. Deterministic Companion Resume

`__companion_open__` is a protocol marker with a known meaning, not a freeform request.
For this marker:

1. Supervisor returns a deterministic continuation plan.
2. Planner preserves that plan without creating an artificial task.
3. Router selects the normal Conversation route.
4. All three nodes still execute and emit their normal runtime instrumentation.
5. None of the three orchestration nodes calls Gemini.

Workspace context and memory still load, so the answer remains grounded in the canonical
focus, currently §3.6 and REV-006.

All other messages retain normal LangGraph routing. Search/corpus requests still reach
Retriever; drafting requests still reach Retriever → Writer.

## 5. Streaming Semantics

The current citation-enforcement path collects the complete first pass before forwarding
text. Change it as follows:

- **Non-academic response:** stream each model chunk immediately.
- **Academic response:** keep the existing buffered citation validation and retry.
- **Companion contract violation:** the first pass may stream; enforcement emits the
  existing `replace` event with the repaired final response.
- **Sources, usage, done and error events:** unchanged.

For a thesis Companion turn, citation enforcement is only wrapped around generation when
the request is classified as academic. Ordinary conversation and the resume marker use
the direct streaming path.

## 6. Error Handling

- Missing model configuration continues to return the existing `503`.
- Vertex errors follow the existing graph/service error path.
- A failed orchestration response keeps current degraded parsing behavior; this change does
  not silently switch providers or models.
- Model names and location remain environment-configurable.
- No partial assistant message is persisted until the turn completes, as today.

## 7. LangGraph Invariants

This change must not remove, reorder or bypass graph nodes. The required topology remains:

```text
START → Supervisor → Planner → Router → Workspace Context → Memory
  ├─ Conversation → END
  ├─ Retriever → Conversation → END
  └─ Retriever → Writer → END
```

The deterministic resume optimization is node-internal. Checkpoints, agent runs, agent
steps, route events and persisted messages remain available.

## 8. Tests

Add or update tests for:

1. Configuration defaults and model-specific factory clients.
2. `build_graph` using the orchestration client exactly three times for ordinary routing.
3. Resume marker using zero orchestration-model calls while executing all graph nodes.
4. Grounded and Writer branches retaining their existing routes.
5. Non-academic citation enforcement emitting the first chunk immediately.
6. Academic citation enforcement retaining buffered retry behavior.
7. Companion repair retaining `replace` semantics.
8. Existing backend, frontend and E2E suites.

Run a deployed live-model smoke for:

- Companion resume;
- ordinary chat;
- grounded source question;
- Writer/drafting request.

Temporary conversations must be deleted after measurement.

## 9. Acceptance Criteria

- Full `make ci` passes.
- Product E2E passes.
- Live Companion resume returns the correct §3.6 context.
- Median local time-to-first-token across three resume turns is at most 5 seconds.
- Median local time-to-first-token across three short ordinary turns is at most 8 seconds.
- Grounded output includes source metadata.
- Writer output still traverses Retriever → Writer.
- No change to public `/chat` or SSE payload contracts.
- No loss of checkpoint, message or runtime-event persistence.

## 10. Out of Scope

- Preview Gemini models.
- Parallel speculative agent execution.
- Removing Supervisor, Planner or Router.
- Replacing LangGraph.
- Provider failover or a model gateway.
- Changes to academic writing, citation or review policy.
