# ThesisOS Product Vision

> **PA0-EWO-001** · Product Constitution Program · Status: **PROPOSED**  
> Pending Gate 1 (Architecture Review) and Gate 2 (Ratification).

---

## One sentence

**ThesisOS is a Research Operating System** — an environment where knowledge, sources,
decisions, and writing form one coherent system, and AI works invisibly to keep it
consistent.

---

## What ThesisOS is

ThesisOS is **not**:

- a chatbot for writing a thesis;
- Notion with AI bolted on;
- a document editor with RAG;
- a single-model assistant tied to one platform.

ThesisOS **is**:

- a **knowledge-centric workspace** for academic research;
- a **product shell** over a qualified runtime (v1.0 Operational);
- a system where **concepts** — not PDFs — sit at the center;
- a place where **context is assembled automatically** so the researcher never builds prompts from scratch;
- a framework whose first application is a thesis, but whose architecture is **project-agnostic**.

When someone asks *"What is ThesisOS?"*, the answer should be:

> *It is where research lives. Sources, concepts, decisions, and writing are one system,
> and AI maintains coherence without being the center of the interface.*

---

## Mission

Enable researchers to **discover, structure, write, and govern** academic knowledge in
one place — with the same rigor as separate tools (Scrivener, Zotero, Obsidian) and the
same intelligence as AI assistants — **without fragmenting the workflow**.

Specifically:

1. **Unify** research, sources, knowledge, writing, and project state.
2. **Hide** engine complexity (memory protocols, corpus rules, governance) behind product surfaces.
3. **Preserve** qualification and traceability inherited from ThesisOS v1.0.
4. **Replace** the LLM without rebuilding the research process.

---

## Positioning

| Layer | Role |
|-------|------|
| **Product** | Workspace the user sees — Research, Writing, Sources, Knowledge, AI panel |
| **Knowledge Engine** | Memory, corpus, decisions, Context Engine, graph — invisible |
| **AI Engine** | Model, prompt wire, inference — swappable |
| **Runtime** | FastAPI, Postgres, LangGraph, retrieval — qualified in v1.0 |

The thesis project (Fashion Design / STIGMATA) is the **first tenant**, not the product definition.

---

## Core beliefs

### 1. Knowledge before documents

Research flows:

```text
Knowledge  →  Sources  →  Writing  →  Output
```

not:

```text
PDF  →  Notes  →  Chapter
```

### 2. Context before prompts

The **Context Engine** assembles what the AI needs from project state, sources, concepts,
and decisions. The user selects an action — not a prompt template.

### 3. AI lateral, not central

Like Copilot beside code: content in the center, AI on the right. Chat remains a
power-user mode, not the default home.

### 4. Governance invisible, present

Memory proposals, frozen decisions, corpus exclusions, and audit trails remain — as
product flows ("Approve change?", "Frozen decision"), not as operator-facing jargon.

### 5. Model independence

Behavior lives in constitution, knowledge, and capability — not in one chat session or
one LLM vendor.

---

## Product modules (workspace)

The user-facing workspace contains five surfaces:

| Module | Purpose |
|--------|---------|
| **Research** | Map and explore the research landscape |
| **Writing** | Outline + editor + contextual AI (Scrivener-class) |
| **Sources** | Sources as objects — metadata, annotations, citations, links |
| **Knowledge** | Concepts once; "Explain this thesis" navigation |
| **AI** | Action panel — rewrite, verify, find sources, compare |

Home invites work: continue where you left off, progress, recent activity — not an admin dashboard.

---

## Relationship to ThesisOS v1.0

v1.0 Operational (`thesisos-v1.0-operational`) delivered a **qualified engine**:

- OR-1…OR-7 + D.1 E2E + E.1 baseline
- Governed knowledge, memory, decisions, academic production
- Documented platform limitations (e.g. W-06)

**Product v2** does not replace the engine. It delivers the **experience** the engine
deserves. All PX milestones must preserve v1.0 qualification as regression baseline.

---

## Success criteria (product)

The product succeeds when a researcher can:

1. Open ThesisOS and **continue writing within minutes** without opening a chat tab.
2. Import a source and **use it in the next paragraph** without manual indexing steps.
3. Click a concept and **see its role across the project** (Explain this thesis).
4. Close a session with **governed state updates** (proposals, not silent writes).
5. Switch LLM **without rebuilding** project knowledge or process.

---

## Non-goals

ThesisOS Product v2 explicitly **does not** aim to:

| Non-goal | Rationale |
|----------|-----------|
| Compete with ChatGPT on open conversation | We compete on **integrated research workflow** |
| Replace Zotero as standalone bibliography manager | Sources are **in-flow**, not a separate app export |
| Be a generic note-taking app | Notes serve **concepts and chapters**, not freeform wiki |
| Auto-publish or ghostwrite theses | Academic integrity; human approval gates remain |
| Multi-user collaboration in v2.0 initial release | PX-6 may explore; not core v2.0 promise |
| Change Runtime Constitution in PA-0 | Product constitution only; cross-plane via P6 |
| Generate engineering program during PA-0 | Execution Authorization is a separate gate |

---

## Product Playbook (operational reference)

Principi prodotto, journey ufficiali (UJ-001–003), metriche permanenti e north star orientato allo studente:
[`product-playbook.md`](product-playbook.md).

This vision document defines **strategic positioning** (Research OS). The playbook defines **how we validate and evolve** the product with user evidence.

---

## Constitution alignment

This vision is governed by:

- `docs/CONSTITUTION-GOVERNANCE.md` — precedence, P8 change policy
- `docs/runtime-constitution.md` — engine invariants (P3 prevails on conflict)
- Product ADR set (ADR-0034…0041) — to be ratified in PA-0

Amendment: new Product Constitution version only per P8 triggers — not per UX tweak.

---

## WO-TRACE

```text
PA0-EWO-001 → docs/product/VISION.md → ADR-0034 (Product Vision) → Gate 1 / Gate 2
```
