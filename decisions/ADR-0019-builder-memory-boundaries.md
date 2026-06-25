# ADR-0019: Builder Memory Boundaries

- Status: Accepted (2026-06-24)
- Context: ASEP Build Control Plane execution workers (legacy: *BuilderOS* — Cursor build-time agents) need a retrieval accelerator so Architect, Planner, Backend, Frontend, QA, and Critic agents can understand project state without reading the entire repository. External agent-memory frameworks (TencentDB Agent Memory, DB-GPT, Letta, Mem0, Zep) optimize conversation-derived memory or full agent runtimes — not a filesystem-first, structured corpus (`knowledge/`, `contracts/`, `decisions/`, `plans/`, `docs/`). ThesisOS M2 runtime memory (ADR-0003, ADR-0015) is a separate concern: domain truth for end users in Cloud SQL, not builder context.
- Decision:
  1. **Filesystem is authoritative.** `knowledge/`, `contracts/`, `decisions/`, `plans/`, `docs/`, and frozen design specs are the source of truth. Builder Memory is **cache-only** and **non-authoritative**.
  2. **Custom hybrid indexer (V1).** Builder Memory lives in `builder_memory/` as a local Python sidecar. Corpus indexing uses **BM25-only** (SQLite FTS5) over an allowlisted path set. **Embeddings deferred** until lexical retrieval proves insufficient. **Mem0 and external memory services rejected for V1.**
  3. **Episodic layer (V1).** Append-only **SQLite** store (`.builder-memory/episodic.sqlite`) for builder session artifacts (lessons learned, task outcomes, failure analyses). No external services.
  4. **Knowledge snapshots.** At each milestone closure, a snapshot manifest is written to `knowledge/snapshots/{milestone}.json` (file hashes + commit SHA) so Builder Memory can compute what changed since the last gate without re-reading the full corpus.
  5. **Allowed operations:**

```yaml
read:
  - knowledge/
  - contracts/
  - decisions/
  - plans/
  - docs/
index: yes
retrieve: yes
rank: yes
snapshot: yes
episodic_append: yes   # session artifacts only; never repo files
```

  6. **Forbidden operations:**

```yaml
edit_files: false
edit_adr: false
edit_contracts: false
edit_code: false
source_of_truth: false
runtime_integration: false   # no hooks into /chat, MemoryService, memory_context_node
```

  7. **Runtime isolation.** `builder_memory/` must not import `backend.app` or share tables with M2 `memories`. Storage is gitignored `.builder-memory/` plus git-tracked `knowledge/snapshots/`.
  8. **Prompt contract.** Every assembled context block is prefixed `NON-AUTHORITATIVE — filesystem wins on conflict` with `Source:` path citations.
- Consequences: Builder agents gain faster onboarding and lower token use without architectural debt from third-party agent runtimes. The cost is maintaining a small custom indexer and snapshot discipline at milestone gates. Embeddings and Mem0 remain available for a future milestone if BM25 retrieval proves inadequate on real usage data.
- Alternatives considered: (a) TencentDB Agent Memory — rejected (session/persona pipeline, unclear license, wrong authority model). (b) DB-GPT — rejected (full framework adoption). (c) Letta — rejected (second agent runtime). (d) Mem0 V1 — rejected (project-memory.md and current-state.md already cover episodic value; YAGNI). (e) Zep/Graphiti — rejected (temporal graph overkill for frozen ADR corpus). (f) Vertex embeddings in V1 — deferred (keyword retrieval sufficient for ADR/contracts/specs naming conventions).
