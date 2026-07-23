# Product Constitution v1.1 — Companion-first Draft

> Successor draft to the frozen Product Constitution v1.0. This file does not edit or
> retroactively replace v1.0; supersession becomes effective only at v1.1 ratification.

## Metadata

| Field | Value |
|-------|-------|
| **Version** | 1.1-draft |
| **Lifecycle** | Draft — Architect-authorized 2026-07-23 |
| **Supersedes on ratification** | Product Constitution v1.0 |
| **Runtime compatibility** | Runtime Constitution v1; ThesisOS v1.x |
| **Primary amendment** | ADR-0045 Companion-first Product Entry |

## Product thesis

ThesisOS is a **Research Operating System**. The Thesis Companion is its default continuity
and orchestration surface: it restores the real project state, then routes work through
Writing, Review, Sources, Knowledge and Research.

The product is companion-first, not chat-only.

## Amendment bundle

| Artifact | Disposition |
|----------|-------------|
| ADR-0034 Product Vision | Inherited |
| ADR-0035 Product Architecture | Inherited |
| ADR-0036 Information Architecture | Superseded only for default-entry invariant |
| ADR-0037 Knowledge Model | Inherited |
| ADR-0038 Context Engine | Inherited |
| ADR-0039 AI Interaction Model | Superseded only for central-entry invariant |
| ADR-0040 Product State | Inherited |
| ADR-0041 Blueprint Runtime Sync | Inherited |
| ADR-0045 Companion-first Product Entry | New, binding on ratification |

## Default experience

```text
Open project
  → Thesis Companion resume
  → Continue current focus or choose a module
  → Writing / Review / Sources / Knowledge / Research
  → Preserve a session artifact
  → Explicitly promote accepted work through product write/review gates
```

Route contract:

| Route | Role |
|-------|------|
| `/` | Thesis Companion — default owned-project entry |
| `/ai` | Compatibility alias / full conversation surface |
| `/writing` | Versioned chapter workspace and contextual AI actions |
| `/review` | Proposal comparison and acceptance |
| `/sources` | Corpus, upload, indexing and bibliography |
| `/knowledge` | Concepts, decisions and thesis knowledge |
| `/research` | Research exploration |

## Non-negotiable boundaries

- No silent chapter mutation from freeform chat.
- No thesis context in demo or unrelated projects.
- No frontend-only academic enforcement.
- No replacement of artifact-centered Writing and Review workflows.
- No claim of v1.1 ratification until the governance gate records it.

## Ratification checklist

- [x] Explicit Architect authorization to open v1.1
- [x] ADR-0045 accepted for the draft
- [x] Companion-first implementation passes full repository CI
- [x] Real continuation turn verified against the owned thesis
- [x] Product E2E covers Companion, Writing, Review, Sources, Knowledge and export
- [ ] Governance validation and v1.1 ratification record
- [ ] Mark v1.0 Superseded and freeze v1.1
