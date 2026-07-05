# RFC-001 — Research Operating System

> **PA0-EWO-002** · Status: **PROPOSED**  
> Request for Comments — exploration and decision requests for Product Constitution.

---

## Summary

Define ThesisOS Product as a **Research Operating System** with a knowledge-centric
workspace, Context Engine, and lateral AI — instead of a chat-first thesis assistant or
a generic productivity suite.

---

## Problem

Academic research today requires **5–8 disconnected tools**:

| Need | Typical tool |
|------|--------------|
| Outline + long-form writing | Scrivener |
| Sources + citations | Zotero |
| Notes + links | Obsidian |
| PDF reading | Reader apps |
| AI assistance | ChatGPT / Claude / NotebookLM |
| Project tracking | Notion / spreadsheets |

Each tool holds partial state. **No single system** owns concepts, sources, decisions,
and prose together with governed memory and qualified runtime behavior.

ThesisOS v1.0 solved **engine and governance** (OR-1…OR-7). It did not solve **operator
experience** — the default surface is still chat.

---

## Proposal

Build a **Research OS** product shell:

```text
Workspace (user sees)
  Research · Writing · Sources · Knowledge · AI panel

Knowledge Engine (hidden)
  Context · Graph · Memory · Decisions · Corpus

AI Engine (swappable)
  Actions · Models · Enforcement

Runtime (qualified v1.0)
  API · DB · Graph · Retrieval
```

**Center of gravity:** knowledge (concepts), not documents or conversation.

---

## Alternative A — Chat-first AI assistant

Keep `/chat` as home. Add commands (`/thesis write`) and sidebar links.

| Pros | Cons |
|------|------|
| Minimal UI work | Competes with ChatGPT on wrong axis |
| Familiar | Perpetuates prompt engineering |
| Fast to ship | Engine remains visible to operator |

**Decision:** Rejected as primary product model. Chat becomes secondary (`/ai` power mode).

---

## Alternative B — Notion-like workspace

Flexible blocks, databases, pages; AI embedded in blocks.

| Pros | Cons |
|------|------|
| Flexible | No academic governance model |
| Popular pattern | Concept singleton hard to enforce |
| Fast iteration | Becomes generic notes app |

**Decision:** Rejected. ThesisOS needs **typed objects** (Source, Concept, Chapter, Decision).

---

## Alternative C — Research OS (recommended)

Fixed module set, knowledge-centric data model, Context Engine, Scrivener-class writing,
Zotero-integrated sources, graph exploration after knowledge exists.

| Pros | Cons |
|------|------|
| Defensible positioning | Larger UX investment |
| Uses v1.0 qualification | PX-1…6 sequential dependency |
| Model-independent | Requires Product Constitution freeze first |
| Matches user mental model ("my research") | |

**Decision:** **Accepted** — basis for Product Constitution v1.0.

---

## Alternative D — Document-centric RAG app

Library upload → chat with PDFs → export text.

| Pros | Cons |
|------|------|
| Simple story | NotebookLM already strong here |
| Reuses retrieval | No writing workspace or decision lifecycle |
| | PDF-at-center contradicts vision |

**Decision:** Rejected. Retrieval remains; **concept graph** is differentiator.

---

## Key trade-offs

| Trade-off | Choice | Rationale |
|-----------|--------|-----------|
| Graph first vs writing first | Writing + Sources before Research graph (PX-2→4→5) | Empty graph has no wow |
| AI central vs lateral | Lateral panel | ADR-0039; Figma/Cursor pattern |
| Constitution vs engineering churn | P8 — engineering program for small changes | Avoid constitution v1.1 for every tweak |
| Auto engineering program after PA-0 | Separate Execution Authorization gate | Planning ≠ ratification |
| Single vs multi-project | Multi-project in PX-6; schema ready in PX-1 | Fashion thesis = template, not hardcode |

---

## Decision requests

| ID | Question | Resolution |
|----|----------|------------|
| DR-1 | Is ThesisOS a Research OS, not a chatbot? | **Yes** — Vision + ADR-0034 |
| DR-2 | Is knowledge-centric model mandatory? | **Yes** — ADR-0037 |
| DR-3 | Is AI lateral mandatory? | **Yes** — ADR-0039 |
| DR-4 | Is Context Engine a first-class subsystem? | **Yes** — ADR-0038 |
| DR-5 | Default home = continue work, not chat? | **Yes** — ADR-0036 |
| DR-6 | Research graph after Knowledge module? | **Yes** — PX-5 after PX-4 |
| DR-7 | Preserve v1.0 OR qualification as regression? | **Yes** — P7 Constitution Governance |

---

## Compatibility

- **Runtime:** `thesisos-v1.0-operational` minimum; no runtime contract break in PA-0.
- **Domain:** First template = academic thesis; blueprint `knowledge/thesis-agent/` remains reference tenant.

---

## Open questions (for Architecture Review)

1. Rich text vs Markdown in Writing editor for v2.0? *(Spec: Markdown first, PX-2)*
2. Italian-first UI vs i18n from PX-1? *(Spec: Italian operator, i18n-ready structure)*
3. Offline draft support? *(PX-6 scope)*

---

## References

- `docs/product/VISION.md`
- `docs/product/specs/thesisos-product-ux-v1.md`
- `docs/CONSTITUTION-GOVERNANCE.md`

---

## WO-TRACE

```text
PA0-EWO-002 → RFC-001 → Gate 1 → ADR-0034…0041
```
