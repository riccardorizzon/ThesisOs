# Mission

> Sources: `docs/superpowers/specs/2026-06-23-thesisos-m0-foundations-design.md` §1–§3, §18; `docs/architecture.md`; ADR-0001, ADR-0010.

## Mission statement

Build a single-user, Cloud-native AgentOS that takes one researcher's thesis from
raw sources to a finished, well-cited document — and do it **milestone by
milestone against frozen contracts**, so the system is always deployable, always
gated, and never accrues architectural debt.

## Operating mission (how we work)

The mission is as much about *method* as product:

1. **Freeze the architecture early; extend, never rewrite.** Every milestone adds
   one vertical slice on top of stable contracts (GraphState, DB schema, ADRs).
   The orchestration seam (LangGraph) was wired in M1 with a single node so that
   M2–M18 *add nodes around it* instead of rewriting `/chat`. (M1 spec §1.)
2. **Contract-First (ADR-0001).** No product feature code exists before its
   architecture and contracts are written and frozen.
3. **Promotion Gates (ADR-0010).** A milestone is "done" only when an explicit,
   machine-checkable YAML gate is fully green — verified with reproducible
   commands and observed output, never self-declared (`docs/m0-promotion.md`,
   `docs/m1-promotion.md`).
4. **Dev = Prod (ADR-0008).** The same container images run locally
   (`docker-compose`) and in production (Cloud Run), so "works locally" means
   "works in prod."
5. **Zero feature debt.** At every gate, the only allowed incompleteness is an
   intentional `NotImplementedError` / `501` stub with a milestone reference.

## Success criteria

- **Short term (M0–M6):** a usable product for a real thesis — chat, memory,
  ingestion, retrieval, tool routing, writing.
- **Medium term (M7–M11):** citations, outline, critic, QA, GCP hardening — a
  trustworthy academic-writing tool.
- **Long term (M12–M18):** multi-agent orchestration, research mode, a
  NotebookLM-like experience, an editable knowledge base with Mem0-style
  extraction, voice, and finally an autonomous assistant.

## Non-negotiable constraints

| Constraint | Source |
|------------|--------|
| Single-user, no auth, no multi-tenancy | ADR-0001, M0 spec §3 |
| Runtime LLM = Vertex AI only, behind LiteLLM | ADR-0002 |
| Python everywhere server-side; TS only in frontend | ADR-0005 |
| Postgres + pgvector is the single source of truth | M0 spec §7 |
| `GraphState` is the one shared graph state object, frozen | ADR-0007 |
| Embeddings model/dimension-tagged for swap | ADR-0002, M0 spec §7 |
| GCP from day one, Terraform-provisioned | ADR-0004 |
