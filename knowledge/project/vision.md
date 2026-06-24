# Vision

> Sources: `README.md`; `docs/architecture.md` §1; `docs/superpowers/specs/2026-06-23-thesisos-m0-foundations-design.md` §1, §18.

## What ThesisOS is

ThesisOS is a **single-user research and thesis-writing AgentOS**. It is an
assistant that helps one researcher take a real thesis from raw sources to a
finished, well-cited document, while progressively becoming a **self-improving
research assistant**.

It combines, in one system:

- **Chat** — a ChatGPT-style conversational interface.
- **Long-term editable memory** — structured, versioned, manually editable
  knowledge about the user, the thesis, concepts, citations, and decisions.
- **Document ingestion** — PDF / EPUB / DOCX parsing into a searchable corpus.
- **Retrieval-Augmented Generation (RAG)** — answers grounded in the corpus.
- **Citation management** — canonical CSL-JSON sources → APA7 / MLA / Chicago.
- **Outline / chapter management** — a tree of chapters with status and content.
- **Multi-agent orchestration** — a Supervisor-led agent graph that plans,
  retrieves, writes, cites, and critiques.

## The north star

> "Evolve, milestone by milestone, into a self-improving research assistant."
> — M0 spec §1

The end state (M18) is an **autonomous research assistant**: it observes the
thesis state, proposes work, executes it through specialized agents, critiques
its own output, and improves — with the human as director, not operator.

## Defining principles

1. **Single-user, no auth.** No multi-tenancy, no accounts table. Every
   architectural choice assumes exactly one user (the thesis author). This keeps
   the system simple and is a *deliberate constraint*, not a temporary shortcut
   (ADR-0001).
2. **Real thesis first.** The primary use case is a **real Italian-language
   thesis**. This is why embeddings use `text-multilingual-embedding-002` (strong
   Italian support) and why the M0–M6 slice is prioritized as a usable product.
3. **Cloud from day one.** It runs on GCP from the first milestone, with dev/prod
   parity, so there is never a "now make it production-ready" rewrite (ADR-0004,
   ADR-0008).
4. **One runtime LLM vendor.** Vertex AI is the only runtime LLM dependency,
   hidden behind a LiteLLM seam so it can be swapped by configuration (ADR-0002).
5. **Contract-first, gate-driven.** Architecture and contracts are frozen before
   features; each milestone passes an explicit, machine-checkable gate before the
   next begins (ADR-0001, ADR-0010).

## Who builds it

ThesisOS is built by **Cursor agents** (the "builder"), coordinated with an
AgentOS methodology (Observe → Hypothesis → Plan → Implement → Test → Critic →
Revise → Promote). The builder is **build-time only**; no deployed code path
calls Cursor (`docs/architecture.md` §2). See `agents/` and `development/`.

## What it is explicitly NOT (today)

- Not multi-user, not a SaaS, not auth-gated.
- Not dependent on any runtime LLM vendor other than Vertex AI.
- Not using an off-the-shelf memory product (Mem0) in its core — memory is custom
  (ADR-0003); Mem0-style auto-extraction is deferred to M15–M16.
- Not a "build agents early" project — orchestration is frozen early as a *seam*,
  but real agents arrive milestone by milestone (M1 spec §1).
