# ThesisOS Product UX — Specification v1

> **PA0-EWO-003** · Status: **PROPOSED** (freeze at Gate 2)  
> Product Specification for Product Constitution v1.0. Implementation: PX-1…PX-6 only after Execution Authorization.

---

## 1. Scope

This spec defines the **Product Plane UX and domain model** for ThesisOS v2. It does not
modify Runtime Constitution invariants. Conflicts resolve per `docs/CONSTITUTION-GOVERNANCE.md` P3.

**In scope:** workspace modules, information architecture, Context Engine, product state,
AI interaction, knowledge model, sync policy, milestone map PX-1…PX-6.

**Out of scope:** PA-0 implementation, runtime graph changes, OR oracle redefinition.

---

## 2. Product thesis

ThesisOS Product = **Research Operating System**. The thesis is the first application template.

See `docs/product/VISION.md` and `docs/product/rfc/RFC-001-research-os.md`.

---

## 3. Architecture layers

User sees layers 1–2 only.

```text
L1  Workspace     Home · Research · Writing · Sources · Knowledge · AI
L2  Knowledge Engine   Context · Graph · Memory · Decisions · Corpus · Bibliography
L3  AI Engine     Model router · Actions · prompt_wire · enforcement
L4  Runtime       FastAPI · Postgres · LangGraph · retrieval (v1.0 qualified)
```

Detailed invariants: ADR-0035 (draft in PA-0).

---

## 4. Information architecture

### 4.1 Sidebar

```text
Home
Research
Writing
Sources
Knowledge
─────────
Settings
```

Deprecated as primary nav: standalone Chat, Memory, Library, Outline, Workspace routes
(absorbed into modules).

### 4.2 Routes

| Route | Module |
|-------|--------|
| `/` | Home |
| `/research`, `/research/[conceptId]` | Research |
| `/writing`, `/writing/[chapterId]` | Writing |
| `/sources`, `/sources/[sourceId]` | Sources |
| `/knowledge`, `/knowledge/[conceptId]` | Knowledge |
| `/ai` | AI (power mode) |
| `/settings` | Settings |

Default entry: **Home**, not `/chat`.

Detailed in ADR-0036.

---

## 5. Workspace modules

### 5.1 Home

Purpose: invite work, not administer.

```text
Progress ("Prima dei dieci minuti" — deterministic from outline + chapter status)
[ Continua → last chapter/section ]
Quick actions: Ricerca · Scrittura · Revisione · Importa documento
Recent activity feed
```

No OR-7 jargon. Pending proposals surfaced as actionable items.

### 5.2 Research (PX-5)

Interactive map of research landscape (ResearchRabbit × Obsidian). Nodes = concepts with
live links to sources, chapters, decisions.

**Dependency:** populated Knowledge graph (PX-4) before rich graph UX.

### 5.3 Writing (PX-2)

Three-panel layout (fixed):

```text
| Outline tree | Markdown editor | AI action panel |
```

- Outline: `chapters` tree, drag reorder, status badges
- Editor: selection-aware; autosave; version history
- AI panel: contextual actions (rewrite, deepen, find sources, verify, compare, summarize)

Scrivener-class structure; AI accompanies, does not replace editor.

### 5.4 Sources (PX-3)

Source as object:

```text
Source → Metadata → Annotations → Extracts → Citations → Concepts → Chapters
```

States: `candidata` → `approvata` → `esclusa` (aligned with Bibliography-Master policy).

Import: drag-drop → parse → index → propose metadata + concepts.

Activates existing `sources`, `citations`, `notes` schema (M7 product track).

### 5.5 Knowledge (PX-4)

**Killer feature:** Explain this thesis — click concept → unified panel:

- Definition, relevance, chapters, supporters, critics, decisions, local graph

Concept **singleton** — one canonical node per concept slug.

Same graph as Research; Knowledge = ontological lens, Research = exploratory lens.

### 5.6 AI panel (PX-2+)

Action runner with pre-assembled Context Packet — not freeform chat as default.

| User context | Default actions |
|--------------|-------------------|
| No selection | Ask, search corpus, project status |
| Text selection | Rewrite, verify, find sources, summarize |
| Chapter open | Draft section, review, outline check |
| Source open | Extract concepts, summarize, link chapter |
| Concept open | Explain, find sources, controversies |

Streaming via existing `/chat` with `context_packet` + `action` parameters (PX-2 EWO).

Detailed in ADR-0039.

---

## 6. Context Engine

Central invisible subsystem (ADR-0038).

### 6.1 Input

```typescript
{
  workspace_id, project_id,
  surface: "writing" | "sources" | "knowledge" | "research" | "home",
  entity_type, entity_id,
  selection?: Range,
  user_intent?: string
}
```

### 6.2 Output — ContextPacket

```typescript
{
  project: { title, phase, progress_pct },
  entity: { type, id, title, snippet? },
  relevant_sources: SourceRef[],
  concepts: ConceptRef[],
  decisions: DecisionRef[],
  definitions: DefinitionRef[],
  citations_available: CitationRef[],
  corpus_constraints: string[],
  writing_rules: string[],
  memory_proposals_pending: number,
  recent_activity: ActivityRef[]
}
```

### 6.3 Assembly precedence

1. Binding decisions (OR-5)
2. Entity scope
3. Retrieval (OR-3, corpus-scoped)
4. Concept neighborhood (1-hop, PX-4+)
5. Terminology definitions
6. Writing rules if `surface=writing`
7. Truncate to token budget

### 6.4 API (PX-1+)

```text
GET  /projects/{id}/context?surface=&entity_type=&entity_id=
POST /ai/actions/{action}  { context_id, params }
```

**PX-1:** minimal packet (chapter + decisions + corpus rules).  
**PX-4+:** graph-aware neighborhood.

UI: **ContextBar** — "12 fonti · 18 concetti · 4 decisioni · 34 citazioni"

---

## 7. Product state model (ADR-0040)

| State | Store | UX surface |
|-------|-------|------------|
| Outline / chapters | `chapters` + blueprint sync | Writing tree |
| Progress | derived | Home ring |
| Decisions frozen/open | memory + Decisions.md | Knowledge, proposals |
| Sources | `sources` + documents | Sources module |
| Concepts | `concepts` + graph edges | Knowledge / Research |
| Session proposals | OR-7 protocol | Modals, not raw protocol text |
| Activity | `activities` | Home feed |

Progress formula: weighted by outline nodes × chapter status (deterministic, not LLM).

---

## 8. Sync policy (ADR-0041)

| Artifact | Source of truth (governance) | Source of truth (runtime UX) |
|----------|-------------------------------|------------------------------|
| Decisions, Terminology | Blueprint markdown | DB memories / concepts |
| Chapters (promoted) | Bidirectional with approval | `chapters` table |
| Bibliography master | Blueprint until operator promotes | `sources` after approval |

Conflict: **operator approval always**. No silent sync.

Blueprint reference tenant: `knowledge/thesis-agent/`.

---

## 9. Design principles

1. Engine invisibility (P1 Product Vision)
2. Context before prompts
3. Knowledge singleton
4. AI lateral (Copilot model)
5. Objects not files
6. Home = action, not dashboard
7. Governance as UX flows
8. Multi-tenant by design (`project_id` from PX-1)

Design system: calm academic tone; references Linear density, Scrivener outline, Notion hierarchy. Desktop-first.

---

## 10. Execution milestones

Blocked until Gate 3 (Execution Authorization).

| Milestone | Deliverables |
|-----------|--------------|
| **PX-1 Foundation** | AppShell, nav, design tokens, Home, routing, Context Engine v0, `project_id` |
| **PX-2 Writing** | Outline tree, editor, AI panel, session flow, chapter state |
| **PX-3 Sources** | Import, metadata, citations, annotations, chapter links |
| **PX-4 Knowledge** | Concept model, Explain panel, concept cards, browser |
| **PX-5 Research** | Graph canvas, discovery, exploration view |
| **PX-6 Polish** | Citation validator (W-06 mitigation), perf, multi-project, export, settings depth |

Sequential dependency: PX-1 → … → PX-6.

---

## 11. Data model extensions (PX-3+)

New entities (product domain):

```text
projects
concepts, concept_relations
concept_sources, concept_chapters, concept_decisions (M:N)
context_packets (cache, optional)
activities
```

Existing activation: `sources`, `citations`, `notes`, `chapters` tree.

---

## 12. Regression and compatibility

- Maintain OR-1…OR-7 qualification on live stack after each PX QWO.
- W-06 remains documented platform limitation until Citation Validator (PX-6).
- Product Constitution compatibility block in manifest:

```yaml
runtime_constitution: v1
minimum_runtime_release: thesisos-v1.0-operational
maximum_runtime_release: thesisos-v1.x
```

---

## 13. Governance references

| Document | Role |
|----------|------|
| `docs/CONSTITUTION-GOVERNANCE.md` | P1–P8 |
| `docs/product/PRODUCT-CONSTITUTION.md` | Manifest SoT |
| `docs/product/CONSTITUTION-PROGRAM-charter.md` | PA-0 / gates |
| ADR-0034…0041 | Frozen invariants (PA-0) |

Constitution change: P8 only. UX iteration → engineering program, not constitution bump.

---

## 14. ADR mapping

| ADR | This spec section |
|-----|-------------------|
| 0034 Product Vision | §2 |
| 0035 Product Architecture | §3 |
| 0036 Information Architecture | §4 |
| 0037 Knowledge Model | §5.5, §11 |
| 0038 Context Engine | §6 |
| 0039 AI Interaction | §5.6 |
| 0040 Product State | §7 |
| 0041 Blueprint Sync | §8 |

---

## WO-TRACE

```text
PA0-EWO-003 → thesisos-product-ux-v1.md → Gate 1 → Gate 2 freeze → PX-n
```
