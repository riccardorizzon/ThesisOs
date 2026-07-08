# Getting started with ThesisOS

ThesisOS is a research writing workspace: import sources, explore concepts, write chapters, and review AI proposals — all grounded in your corpus.

## Prerequisites

- Docker (for local stack) or a deployed backend URL
- Node 20+ and Python 3.12 for development

```bash
make install   # backend venv + frontend deps
make up        # PostgreSQL, backend :8000, frontend :3000
```

Open [http://localhost:3000](http://localhost:3000).

## First-run workflow

1. **Home** — check progress ring and use **Importa documento** to add your first source.
2. **Sources** (`/sources`) — browse the bibliography, search, export BibTeX.
3. **Knowledge** (`/knowledge`) — explore concepts linked to sources.
4. **Writing** (`/writing`) — three-panel editor: outline, markdown, AI/context rail.
5. **Review** (`/review`) — accept or reject writing proposals chapter by chapter.
6. **AI** (`/ai`) — persistent chat threads grounded in project context.

## When the corpus is empty

If Sources or Knowledge show an empty state:

- Use **Importa documento** (`/sources/upload`) to upload a PDF or Markdown file.
- Wait for indexing (see banner in Writing when documents are processing).
- Refresh Sources — seeded migration data appears after first `make up` with migrations.

API errors show a **Riprova** button — ensure the backend is running (`make up` or check `/health`).

## Quality gates (developers)

```bash
make ci                              # full gate
make dogfood-m7                      # API + Playwright product flow
cd tests/e2e && npx playwright test m7-product-flow.spec.ts
```

## Next steps

- Research canvas: `/research/canvas`
- Settings and project context: `/settings`
- Architecture and governance: `docs/` and `AGENTS.md`
