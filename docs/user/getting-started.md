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

1. **Thesis Companion** (`/`) — read the real project resume and continue the current focus.
2. **Chat** — ask, search the corpus, review a direction, draft, or preserve the session.
3. **Writing** (`/writing`) — edit versioned chapters in the three-panel workspace.
4. **Manoscritto** (`/manuscript`) — read the thesis in order; open Writing to edit.
5. **Review** (`/review`) — accept or reject writing proposals chapter by chapter.
6. **Sources** (`/sources`) — upload, browse, search, index and export the bibliography.
7. **Knowledge** (`/knowledge`) — explore concepts, decisions and source relationships.

The Companion can preserve a proposal for continuity, but it does not silently overwrite a
chapter. Promote definitive text through Writing and Review.

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
- Settings (`/settings`) — project prefs, export options, **beta limitations** panel
- Demo runbook (presenters): `docs/demo/DEMO-SCRIPT.md` and `docs/demo/DEMO-HANDOUT.md`
- Companion-first governance draft: `docs/product/PRODUCT-CONSTITUTION-v1.1-DRAFT.md`
- Architecture and governance: `docs/` and `AGENTS.md`
