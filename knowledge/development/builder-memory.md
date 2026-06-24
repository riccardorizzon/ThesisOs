# Builder Memory (ADR-0019)

Retrieval-only sidecar for **BuilderOS** Cursor agents. Not part of ThesisOS runtime.

## Principles

- **Filesystem is authoritative** — `knowledge/`, `contracts/`, `decisions/`, `plans/`, `docs/`
- **Builder Memory is cache-only** — every prompt block is `NON-AUTHORITATIVE`
- **V1:** BM25-only (SQLite FTS5), SQLite episodic store, no Mem0, no embeddings

## Setup

```bash
cd builder_memory
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Commands

```bash
# From repo root (with venv activated or full path to builder-memory)
builder-memory index              # full index
builder-memory index --incremental
builder-memory status
builder-memory retrieve --task "GraphState frozen" --role architect --budget 8000
builder-memory snapshot --milestone m2-complete   # at milestone gate
builder-memory episodic-append --type task_outcome --summary "..." --ref plans/builder/STATE.yaml
```

## Integration

Before `orchestrate-builders wave`, run:

```bash
.cursor/skills/orchestrate-builders/scripts/builder-memory-preflight.sh
```

Inject `builder-memory retrieve` output into agent prompts (see orchestrate-builders skill).

## Storage

| Path | Purpose | Git |
|------|---------|-----|
| `.builder-memory/` | BM25 index + episodic SQLite | ignored |
| `knowledge/snapshots/` | Milestone hash manifests | tracked |

### Retrieval provenance

Every result includes structured provenance for the Critic Agent:

```yaml
path: decisions/ADR-0017-memory-versioning.md
score: 0.91
source_type: adr
```

Printed as YAML block after `builder-memory retrieve`.

## Rankers (M3 extension)

See `builder_memory/rankers/README.md` — V1 uses BM25 only; future: recency, milestone proximity, hybrid embeddings.
