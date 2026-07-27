# Manoscritto Reader Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a read-only Manoscritto module (`/manuscript`) with ordered TOC (chapters + heading sections, status, word counts), chapter reader, Prev/Next, and Modifica → Writing.

**Architecture:** Product-plane frontend only. Reuse `chapterClient` and `parseMarkdownSections`. No new backend APIs. Two-panel workspace (TOC | reader). Edit never happens in Manoscritto — Modifica routes to `/writing/[chapterId]`. ADR-0036 amended for six primary modules + Settings (Manoscritto inserted after Writing).

**Tech Stack:** Next.js 15 App Router, React 19, TypeScript, Vitest + Testing Library, existing Tailwind tokens (`ink`, `surface`, `accent`, `StatusBadge`).

**Spec:** `docs/superpowers/specs/2026-07-27-thesisos-manuscript-reader-design.md`

## Global Constraints

- Manoscritto is **read-only** in v1 — no inline editor, no PATCH from this module.
- **Modifica** must navigate to `/writing/[chapterId]` (never stay on manuscript to edit).
- No new chapter/section backend endpoints.
- Sections = client parse of `#`…`######` via existing `parseMarkdownSections`.
- Do **not** add Review / AI / Revisiona buttons in v1 (follow-up: `/review?chapter=`).
- Do **not** remove or hollow out Writing.
- IA change ships with ADR-0036 amendment in the same change set as nav.
- Prefer Italian UI copy consistent with Writing/Review (e.g. “Modifica”, “Ancora vuoto”).
- Do not commit unless the user explicitly requests a commit.
- Match existing test patterns (`vitest`, `@testing-library/react`, `data-testid`).

## File Map

| Path | Responsibility |
|------|----------------|
| `decisions/ADR-0036-information-architecture.md` | Amend nav + INV-IA-1 for Manoscritto |
| `frontend/lib/nav.ts` | PRIMARY_NAV entry + breadcrumbs |
| `frontend/lib/routes.ts` | PRODUCT_ROUTES + ProductModule |
| `frontend/lib/nav.test.ts` | IA assertions |
| `frontend/lib/routes.test.ts` | Route registry assertions |
| `frontend/lib/manuscriptToc.ts` | Pure TOC build (order, sections, totals) |
| `frontend/lib/manuscriptToc.test.ts` | Unit tests for TOC helpers |
| `frontend/components/manuscript/ManuscriptMarkdown.tsx` | Read-only markdown → HTML-ish React |
| `frontend/components/manuscript/ManuscriptMarkdown.test.tsx` | Renderer + heading ids |
| `frontend/components/manuscript/ManuscriptToc.tsx` | Left panel UI |
| `frontend/components/manuscript/ManuscriptToc.test.tsx` | TOC interactions |
| `frontend/components/manuscript/ManuscriptReader.tsx` | Right panel + actions |
| `frontend/components/manuscript/ManuscriptReader.test.tsx` | Prev/Next/Modifica |
| `frontend/components/manuscript/ManuscriptWorkspace.tsx` | Load chapters, selection, wiring |
| `frontend/components/manuscript/ManuscriptWorkspace.test.tsx` | Integration of load + nav |
| `frontend/components/manuscript/index.ts` | Barrel exports |
| `frontend/app/manuscript/page.tsx` | `/manuscript` |
| `frontend/app/manuscript/[chapterId]/page.tsx` | Deep link |
| `tests/e2e/px1-ui-smoke.spec.ts` | Sidebar label list |

---

### Task 1: Information architecture — Manoscritto in nav and routes

**Files:**
- Modify: `decisions/ADR-0036-information-architecture.md`
- Modify: `frontend/lib/nav.ts`
- Modify: `frontend/lib/routes.ts`
- Modify: `frontend/lib/nav.test.ts`
- Modify: `frontend/lib/routes.test.ts`
- Modify: `tests/e2e/px1-ui-smoke.spec.ts`

**Interfaces:**
- Produces: `PRIMARY_NAV` entry `{ href: "/manuscript", label: "Manoscritto", group: "primary" }` between Writing and Sources
- Produces: `ProductModule` includes `"manuscript"`
- Produces: `PRODUCT_ROUTES` entries for `/manuscript` and `/manuscript` deep-link documentation path `/manuscript` (chapter path optional in registry — at minimum `/manuscript`)

- [ ] **Step 1: Write the failing nav/route tests**

Update `frontend/lib/nav.test.ts`:

```ts
it("matches ADR-0036 sidebar (six primary modules + Settings)", () => {
  const labels = PRIMARY_NAV.map((r) => r.label);
  expect(labels).toEqual([
    "Home",
    "Research",
    "Writing",
    "Manoscritto",
    "Sources",
    "Knowledge",
    "Settings",
  ]);
});

it("has exactly one settings route", () => {
  expect(PRIMARY_NAV.filter((r) => r.group === "settings")).toHaveLength(1);
  expect(PRIMARY_NAV.filter((r) => r.group === "primary")).toHaveLength(6);
});
```

Add breadcrumb case:

```ts
expect(buildBreadcrumbs("/manuscript")).toEqual([{ label: "Manoscritto" }]);
expect(buildBreadcrumbs("/manuscript/ch-1")).toEqual([
  { label: "Manoscritto", href: "/manuscript" },
  { label: "ch 1" },
]);
```

Update `frontend/lib/routes.test.ts` to expect `/manuscript` in paths and module `"manuscript"`.

Update `tests/e2e/px1-ui-smoke.spec.ts` `SIDEBAR_LABELS` to insert `"Manoscritto"` after `"Writing"`.

- [ ] **Step 2: Run tests to verify RED**

```bash
cd frontend && npm test -- lib/nav.test.ts lib/routes.test.ts
```

Expected: FAIL — labels still missing Manoscritto / primary length still 5.

- [ ] **Step 3: Implement ADR + nav + routes**

In `ADR-0036`:
- Add Manoscritto to the sidebar ASCII diagram between Writing and Sources.
- Add routes `/manuscript`, `/manuscript/[chapterId]` to the route map table (module Manoscritto).
- Rewrite **INV-IA-1** to: sidebar contains exactly these six primary modules + Settings: Home, Research, Writing, Manoscritto, Sources, Knowledge (no Memory/Corpus/Chat as top-level).
- Note amendment date and that Review/AI remain adjuncts.

In `frontend/lib/nav.ts`:
- Insert `{ href: "/manuscript", label: "Manoscritto", group: "primary" }` after Writing.
- Update the INV-IA-1 comment to six primary + Settings.

In `frontend/lib/routes.ts`:
- Extend `ProductModule` with `"manuscript"`.
- Add:

```ts
{
  path: "/manuscript",
  module: "manuscript",
  milestone: "PX-2",
  description: "Manuscript reader — ordered thesis reading",
},
{
  path: "/manuscript/[chapterId]",
  module: "manuscript",
  milestone: "PX-2",
  description: "Manuscript reader focused on one chapter",
},
```

(Place after writing routes.)

- [ ] **Step 4: Run tests to verify GREEN**

```bash
cd frontend && npm test -- lib/nav.test.ts lib/routes.test.ts
```

Expected: PASS.

- [ ] **Step 5: Commit** (only if user requested commits)

```bash
git add decisions/ADR-0036-information-architecture.md \
  frontend/lib/nav.ts frontend/lib/routes.ts \
  frontend/lib/nav.test.ts frontend/lib/routes.test.ts \
  tests/e2e/px1-ui-smoke.spec.ts
git commit -m "$(cat <<'EOF'
feat(ia): add Manoscritto primary nav module (ADR-0036)

EOF
)"
```

---

### Task 2: Pure TOC helpers

**Files:**
- Create: `frontend/lib/manuscriptToc.ts`
- Create: `frontend/lib/manuscriptToc.test.ts`

**Interfaces:**
- Consumes: `Chapter` from `@/lib/chapterClient`; `parseMarkdownSections`, `MarkdownSection` from `@/components/writing/MarkdownEditor`
- Produces:

```ts
export type ManuscriptTocSection = {
  id: string;
  label: string;
  level: number;
};

export type ManuscriptTocChapter = {
  id: string;
  title: string;
  status: Chapter["status"];
  word_count: number;
  order_index: number;
  sections: ManuscriptTocSection[];
};

export function sortChaptersByOrder(chapters: Chapter[]): Chapter[];
export function buildManuscriptToc(chapters: Chapter[]): ManuscriptTocChapter[];
export function totalWordCount(chapters: Chapter[]): number;
export function neighborChapterIds(
  orderedIds: string[],
  currentId: string
): { prevId: string | null; nextId: string | null };
```

- [ ] **Step 1: Write the failing unit tests**

```ts
import { describe, expect, it } from "vitest";
import type { Chapter } from "./chapterClient";
import {
  buildManuscriptToc,
  neighborChapterIds,
  sortChaptersByOrder,
  totalWordCount,
} from "./manuscriptToc";

function ch(partial: Partial<Chapter> & Pick<Chapter, "id" | "title" | "order_index">): Chapter {
  return {
    parent_id: null,
    status: "draft",
    content_md: null,
    summary: null,
    word_count: 0,
    version: 1,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
    ...partial,
  };
}

describe("sortChaptersByOrder", () => {
  it("orders by order_index ascending", () => {
    const sorted = sortChaptersByOrder([
      ch({ id: "b", title: "B", order_index: 2 }),
      ch({ id: "a", title: "A", order_index: 0 }),
    ]);
    expect(sorted.map((c) => c.id)).toEqual(["a", "b"]);
  });
});

describe("buildManuscriptToc", () => {
  it("includes status, words, and parsed sections in order", () => {
    const toc = buildManuscriptToc([
      ch({
        id: "1",
        title: "Intro",
        order_index: 0,
        status: "review",
        word_count: 12,
        content_md: "# Alpha\n\n## Beta\n\ntext",
      }),
    ]);
    expect(toc).toHaveLength(1);
    expect(toc[0].status).toBe("review");
    expect(toc[0].word_count).toBe(12);
    expect(toc[0].sections.map((s) => s.label)).toEqual(["Alpha", "Beta"]);
    expect(toc[0].sections[1].level).toBe(2);
  });

  it("uses empty sections when content_md is null", () => {
    const toc = buildManuscriptToc([ch({ id: "1", title: "Empty", order_index: 0 })]);
    expect(toc[0].sections).toEqual([]);
  });
});

describe("totalWordCount", () => {
  it("sums word_count", () => {
    expect(
      totalWordCount([
        ch({ id: "1", title: "A", order_index: 0, word_count: 10 }),
        ch({ id: "2", title: "B", order_index: 1, word_count: 5 }),
      ])
    ).toBe(15);
  });
});

describe("neighborChapterIds", () => {
  it("returns prev/next and nulls at ends", () => {
    expect(neighborChapterIds(["a", "b", "c"], "b")).toEqual({
      prevId: "a",
      nextId: "c",
    });
    expect(neighborChapterIds(["a", "b"], "a").prevId).toBeNull();
    expect(neighborChapterIds(["a", "b"], "b").nextId).toBeNull();
    expect(neighborChapterIds(["a"], "missing")).toEqual({
      prevId: null,
      nextId: null,
    });
  });
});
```

- [ ] **Step 2: Run test to verify RED**

```bash
cd frontend && npm test -- lib/manuscriptToc.test.ts
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement helpers**

```ts
// frontend/lib/manuscriptToc.ts
import type { Chapter } from "@/lib/chapterClient";
import { parseMarkdownSections } from "@/components/writing/MarkdownEditor";

export type ManuscriptTocSection = {
  id: string;
  label: string;
  level: number;
};

export type ManuscriptTocChapter = {
  id: string;
  title: string;
  status: Chapter["status"];
  word_count: number;
  order_index: number;
  sections: ManuscriptTocSection[];
};

export function sortChaptersByOrder(chapters: Chapter[]): Chapter[] {
  return [...chapters].sort((a, b) => a.order_index - b.order_index);
}

export function buildManuscriptToc(chapters: Chapter[]): ManuscriptTocChapter[] {
  return sortChaptersByOrder(chapters).map((chapter) => {
    const sections = parseMarkdownSections(chapter.content_md ?? "").map((s) => ({
      id: s.id,
      label: s.label,
      level: s.level,
    }));
    return {
      id: chapter.id,
      title: chapter.title,
      status: chapter.status,
      word_count: chapter.word_count,
      order_index: chapter.order_index,
      sections,
    };
  });
}

export function totalWordCount(chapters: Chapter[]): number {
  return chapters.reduce((sum, c) => sum + (c.word_count ?? 0), 0);
}

export function neighborChapterIds(
  orderedIds: string[],
  currentId: string
): { prevId: string | null; nextId: string | null } {
  const index = orderedIds.indexOf(currentId);
  if (index < 0) return { prevId: null, nextId: null };
  return {
    prevId: index > 0 ? orderedIds[index - 1]! : null,
    nextId: index < orderedIds.length - 1 ? orderedIds[index + 1]! : null,
  };
}
```

- [ ] **Step 4: Run test to verify GREEN**

```bash
cd frontend && npm test -- lib/manuscriptToc.test.ts
```

Expected: PASS.

- [ ] **Step 5: Commit** (only if user requested)

```bash
git add frontend/lib/manuscriptToc.ts frontend/lib/manuscriptToc.test.ts
git commit -m "feat(manuscript): add TOC ordering and section helpers"
```

---

### Task 3: Read-only markdown renderer

**Files:**
- Create: `frontend/components/manuscript/ManuscriptMarkdown.tsx`
- Create: `frontend/components/manuscript/ManuscriptMarkdown.test.tsx`

**Interfaces:**
- Consumes: `sectionIdFromHeading` from `@/components/writing/MarkdownEditor`
- Produces: `ManuscriptMarkdown({ content: string; className?: string })`
- Heading elements must use `id={sectionIdFromHeading(label)}` so TOC section clicks can `scrollIntoView` / hash-navigate.

**Scope of markdown (v1, no new npm deps):**
- ATX headings `#`–`######`
- Paragraphs (blank-line separated)
- Unordered list lines starting with `- ` or `* `
- Fenced code blocks ` ``` `
- Escape all text with a small `escapeHtml` then render via React text nodes (no `dangerouslySetInnerHTML` for body text). Prefer React elements over HTML strings.

- [ ] **Step 1: Write the failing tests**

```tsx
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { sectionIdFromHeading } from "@/components/writing/MarkdownEditor";
import { ManuscriptMarkdown } from "./ManuscriptMarkdown";

afterEach(() => cleanup());

describe("ManuscriptMarkdown", () => {
  it("renders headings with stable section ids", () => {
    render(<ManuscriptMarkdown content={"# Intro\n\n## Method\n\nHello world."} />);
    const h1 = screen.getByRole("heading", { level: 1, name: "Intro" });
    expect(h1.id).toBe(sectionIdFromHeading("Intro"));
    expect(screen.getByRole("heading", { level: 2, name: "Method" }).id).toBe(
      sectionIdFromHeading("Method")
    );
    expect(screen.getByText("Hello world.")).toBeTruthy();
  });

  it("renders empty content without crashing", () => {
    const { container } = render(<ManuscriptMarkdown content="" />);
    expect(container.querySelector("[data-testid='manuscript-markdown']")).toBeTruthy();
  });
});
```

- [ ] **Step 2: Run test to verify RED**

```bash
cd frontend && npm test -- components/manuscript/ManuscriptMarkdown.test.tsx
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement renderer**

Implement a line-oriented parser in `ManuscriptMarkdown.tsx`:
- `"use client"` not required if no hooks — keep as server-safe function component.
- Root: `<div data-testid="manuscript-markdown" className={cn("prose-like space-y-3 …", className)}>`
- Use existing typography tokens (`text-ink`, `text-lg`, etc.) — do **not** add Tailwind Typography plugin.
- Map heading level → `h1`…`h6` with matching `id`.

- [ ] **Step 4: Run test to verify GREEN**

```bash
cd frontend && npm test -- components/manuscript/ManuscriptMarkdown.test.tsx
```

Expected: PASS.

- [ ] **Step 5: Commit** (only if user requested)

```bash
git add frontend/components/manuscript/ManuscriptMarkdown.tsx \
  frontend/components/manuscript/ManuscriptMarkdown.test.tsx
git commit -m "feat(manuscript): add read-only markdown renderer"
```

---

### Task 4: ManuscriptToc component

**Files:**
- Create: `frontend/components/manuscript/ManuscriptToc.tsx`
- Create: `frontend/components/manuscript/ManuscriptToc.test.tsx`

**Interfaces:**
- Consumes: `ManuscriptTocChapter`, `totalWordCount` types/helpers; `StatusBadge`
- Produces:

```ts
export type ManuscriptTocProps = {
  chapters: ManuscriptTocChapter[];
  activeChapterId: string | null;
  activeSectionId?: string | null;
  onSelectChapter: (chapterId: string) => void;
  onSelectSection: (chapterId: string, sectionId: string) => void;
};
```

- [ ] **Step 1: Write the failing tests**

```tsx
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ManuscriptToc } from "./ManuscriptToc";
import type { ManuscriptTocChapter } from "@/lib/manuscriptToc";

afterEach(() => cleanup());

const chapters: ManuscriptTocChapter[] = [
  {
    id: "c1",
    title: "Capitolo 1",
    status: "draft",
    word_count: 100,
    order_index: 0,
    sections: [
      { id: "intro", label: "Intro", level: 1 },
      { id: "method", label: "Method", level: 2 },
    ],
  },
  {
    id: "c2",
    title: "Capitolo 2",
    status: "approved",
    word_count: 50,
    order_index: 1,
    sections: [],
  },
];

describe("ManuscriptToc", () => {
  it("shows summary, statuses, words, and sections", () => {
    render(
      <ManuscriptToc
        chapters={chapters}
        activeChapterId="c1"
        onSelectChapter={vi.fn()}
        onSelectSection={vi.fn()}
      />
    );
    expect(screen.getByTestId("manuscript-toc")).toBeTruthy();
    expect(screen.getByText(/2 capitoli/i)).toBeTruthy();
    expect(screen.getByText(/150/)).toBeTruthy(); // total words
    expect(screen.getByTestId("status-badge-draft")).toBeTruthy();
    expect(screen.getByText("Intro")).toBeTruthy();
    expect(screen.getByText("Method")).toBeTruthy();
  });

  it("notifies chapter and section selection", () => {
    const onSelectChapter = vi.fn();
    const onSelectSection = vi.fn();
    render(
      <ManuscriptToc
        chapters={chapters}
        activeChapterId="c1"
        onSelectChapter={onSelectChapter}
        onSelectSection={onSelectSection}
      />
    );
    fireEvent.click(screen.getByRole("button", { name: /Capitolo 2/i }));
    expect(onSelectChapter).toHaveBeenCalledWith("c2");
    fireEvent.click(screen.getByRole("button", { name: "Method" }));
    expect(onSelectSection).toHaveBeenCalledWith("c1", "method");
  });
});
```

- [ ] **Step 2: Run RED**

```bash
cd frontend && npm test -- components/manuscript/ManuscriptToc.test.tsx
```

- [ ] **Step 3: Implement TOC UI**

- `nav` with `aria-label="Indice manoscritto"` and `data-testid="manuscript-toc"`
- Header: `{n} capitoli · {total} parole` (Italian)
- Chapter row: title button, `StatusBadge`, word_count
- Nested section buttons with indent by `level` (`pl-3` * level or similar)
- Active chapter: accent/background highlight via `data-active` or class
- Width ~280px owned by parent flex; TOC itself `overflow-y-auto h-full`

Reuse `StatusBadge` from `@/components/ui/StatusBadge`.

- [ ] **Step 4: Run GREEN**

```bash
cd frontend && npm test -- components/manuscript/ManuscriptToc.test.tsx
```

- [ ] **Step 5: Commit** (only if user requested)

---

### Task 5: ManuscriptReader component

**Files:**
- Create: `frontend/components/manuscript/ManuscriptReader.tsx`
- Create: `frontend/components/manuscript/ManuscriptReader.test.tsx`

**Interfaces:**
- Consumes: `Chapter`, `ManuscriptMarkdown`, `StatusBadge`, `neighborChapterIds` results
- Produces:

```ts
export type ManuscriptReaderProps = {
  chapter: Chapter | null;
  prevId: string | null;
  nextId: string | null;
  emptyThesis?: boolean;
  onNavigate: (chapterId: string) => void;
  /** Called when user chooses Modifica — parent routes to Writing */
  onEdit: (chapterId: string) => void;
  scrollToSectionId?: string | null;
};
```

- [ ] **Step 1: Write the failing tests**

```tsx
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { Chapter } from "@/lib/chapterClient";
import { ManuscriptReader } from "./ManuscriptReader";

afterEach(() => cleanup());

const chapter: Chapter = {
  id: "c2",
  parent_id: null,
  order_index: 1,
  title: "Capitolo 2",
  status: "draft",
  content_md: "# Hello\n\nBody.",
  summary: null,
  word_count: 2,
  version: 1,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

describe("ManuscriptReader", () => {
  it("renders title, markdown, and navigates prev/next/edit", () => {
    const onNavigate = vi.fn();
    const onEdit = vi.fn();
    render(
      <ManuscriptReader
        chapter={chapter}
        prevId="c1"
        nextId="c3"
        onNavigate={onNavigate}
        onEdit={onEdit}
      />
    );
    expect(screen.getByTestId("manuscript-reader")).toBeTruthy();
    expect(screen.getByRole("heading", { name: "Capitolo 2" })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: /Precedente|Prev/i }));
    expect(onNavigate).toHaveBeenCalledWith("c1");
    fireEvent.click(screen.getByRole("button", { name: /Successivo|Next/i }));
    expect(onNavigate).toHaveBeenCalledWith("c3");
    fireEvent.click(screen.getByRole("link", { name: /Modifica/i }));
    // Prefer <Link href="/writing/c2"> for real navigation; if button+onEdit, assert onEdit
  });

  it("shows empty thesis CTA", () => {
    render(
      <ManuscriptReader
        chapter={null}
        prevId={null}
        nextId={null}
        emptyThesis
        onNavigate={vi.fn()}
        onEdit={vi.fn()}
      />
    );
    expect(screen.getByRole("link", { name: /Writing|Scrivi/i })).toBeTruthy();
  });

  it("shows empty chapter message when content missing", () => {
    render(
      <ManuscriptReader
        chapter={{ ...chapter, content_md: "" }}
        prevId={null}
        nextId={null}
        onNavigate={vi.fn()}
        onEdit={vi.fn()}
      />
    );
    expect(screen.getByText(/Ancora vuoto/i)).toBeTruthy();
  });
});
```

**Modifica contract (lock this in the test):** use Next.js `Link` with `href={`/writing/${chapter.id}`}` and accessible name `Modifica`. Also call `onEdit` optional — but **href must be present** so middle-click/open-in-new-tab works. Prefer:

```tsx
<Link href={`/writing/${chapter.id}`} data-testid="manuscript-edit">
  Modifica
</Link>
```

Button labels: Italian **Precedente** / **Successivo** (or short **←** / **→** with `aria-label`). Disable when `prevId`/`nextId` is null.

- [ ] **Step 2: Run RED**

```bash
cd frontend && npm test -- components/manuscript/ManuscriptReader.test.tsx
```

- [ ] **Step 3: Implement reader**

- Header row: title, `StatusBadge`, word count, action cluster
- `ManuscriptMarkdown` for body when `content_md` non-empty
- `useEffect` when `scrollToSectionId` set: `document.getElementById(id)?.scrollIntoView({ block: "start" })`
- Empty thesis: copy + `Link` to `/writing`
- No textarea, no `MarkdownEditor`

- [ ] **Step 4: Run GREEN**

```bash
cd frontend && npm test -- components/manuscript/ManuscriptReader.test.tsx
```

- [ ] **Step 5: Commit** (only if user requested)

---

### Task 6: ManuscriptWorkspace + App Router pages

**Files:**
- Create: `frontend/components/manuscript/ManuscriptWorkspace.tsx`
- Create: `frontend/components/manuscript/ManuscriptWorkspace.test.tsx`
- Create: `frontend/components/manuscript/index.ts`
- Create: `frontend/app/manuscript/page.tsx`
- Create: `frontend/app/manuscript/[chapterId]/page.tsx`

**Interfaces:**
- Consumes: `chapterClient.list`, `chapterClient.get`, TOC helpers, Toc + Reader
- Produces: `ManuscriptWorkspace({ chapterId?: string | null })`

**Load algorithm (spec):**
1. `chapterClient.list()` for project (includes `content_md` per chapter)
2. For any chapter still missing content, `chapterClient.get(id)` once and merge into cache
3. `buildManuscriptToc(cached)`
4. Active id = prop `chapterId` if present in list, else first ordered id, else null
5. On select chapter: `router.push(`/manuscript/${id}`)` (keep URL in sync)
6. On select section: navigate to chapter then set `scrollToSectionId`
7. Modifica is Link inside Reader (workspace need not intercept)

- [ ] **Step 1: Write the failing workspace test**

```tsx
import { cleanup, render, screen, waitFor, fireEvent } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ManuscriptWorkspace } from "./ManuscriptWorkspace";

const push = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push, replace: vi.fn() }),
}));

vi.mock("@/lib/chapterClient", () => ({
  chapterClient: {
    list: vi.fn(),
    get: vi.fn(),
  },
  ChapterApiError: class ChapterApiError extends Error {
    status = 404;
    code = "not_found";
  },
}));

import { chapterClient } from "@/lib/chapterClient";

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("ManuscriptWorkspace", () => {
  beforeEach(() => {
    vi.mocked(chapterClient.list).mockResolvedValue([
      {
        id: "c1",
        parent_id: null,
        order_index: 0,
        title: "Uno",
        status: "draft",
        content_md: null,
        summary: null,
        word_count: 3,
        version: 1,
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
      },
      {
        id: "c2",
        parent_id: null,
        order_index: 1,
        title: "Due",
        status: "review",
        content_md: null,
        summary: null,
        word_count: 4,
        version: 1,
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
      },
    ]);
    vi.mocked(chapterClient.get).mockImplementation(async (id: string) => ({
      id,
      parent_id: null,
      order_index: id === "c1" ? 0 : 1,
      title: id === "c1" ? "Uno" : "Due",
      status: id === "c1" ? "draft" : "review",
      content_md:
        id === "c1" ? "# Alpha\n\ntext" : "# Beta\n\nmore words here",
      summary: null,
      word_count: id === "c1" ? 3 : 4,
      version: 1,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    }));
  });

  it("loads TOC sections from fetched content and links Modifica to Writing", async () => {
    render(<ManuscriptWorkspace chapterId="c1" />);
    await waitFor(() => {
      expect(screen.getByText("Alpha")).toBeTruthy();
    });
    expect(screen.getByTestId("manuscript-workspace")).toBeTruthy();
    const edit = screen.getByTestId("manuscript-edit");
    expect(edit.getAttribute("href")).toBe("/writing/c1");
  });

  it("Prev/Next push manuscript routes in order", async () => {
    render(<ManuscriptWorkspace chapterId="c1" />);
    await waitFor(() => screen.getByTestId("manuscript-reader"));
    fireEvent.click(screen.getByRole("button", { name: /Successivo/i }));
    expect(push).toHaveBeenCalledWith("/manuscript/c2");
  });
});
```

- [ ] **Step 2: Run RED**

```bash
cd frontend && npm test -- components/manuscript/ManuscriptWorkspace.test.tsx
```

- [ ] **Step 3: Implement workspace + pages**

`ManuscriptWorkspace.tsx`:
- `"use client"`
- Layout: `flex` row, TOC `w-[280px] shrink-0 border-r`, reader `flex-1 min-w-0`
- Mobile: TOC in a collapsible panel (button “Indice”) — minimal; mirror Writing’s mobile toggle pattern if cheap, else drawer with `hidden md:block` + top button
- Loading: short muted “Caricamento manoscritto…”
- Error: message + retry button calling reload
- Unknown `chapterId`: show alert + fall back to first chapter (and `replace` URL)

`frontend/app/manuscript/page.tsx`:

```tsx
import { ManuscriptWorkspace } from "@/components/manuscript";

export default function ManuscriptPage() {
  return <ManuscriptWorkspace />;
}
```

`frontend/app/manuscript/[chapterId]/page.tsx`:

```tsx
import { ManuscriptWorkspace } from "@/components/manuscript";

type Props = { params: Promise<{ chapterId: string }> };

export default async function ManuscriptChapterPage({ params }: Props) {
  const { chapterId } = await params;
  return <ManuscriptWorkspace chapterId={chapterId} />;
}
```

`index.ts` barrel-export workspace, toc, reader, markdown.

- [ ] **Step 4: Run GREEN**

```bash
cd frontend && npm test -- components/manuscript/
```

Expected: all manuscript component tests PASS.

- [ ] **Step 5: Commit** (only if user requested)

```bash
git add frontend/components/manuscript frontend/app/manuscript
git commit -m "feat(manuscript): add Manoscritto workspace and routes"
```

---

### Task 7: Verification sweep + future hook note

**Files:**
- Modify (if still stale): `docs/superpowers/specs/2026-07-27-thesisos-manuscript-reader-design.md` follow-ups (Revisiona already documented)
- Touch only if tests fail elsewhere after IA change (e.g. CommandPalette snapshots — should auto-pick PRIMARY_NAV)

- [ ] **Step 1: Run focused frontend suite**

```bash
cd frontend && npm test -- lib/nav.test.ts lib/routes.test.ts lib/manuscriptToc.test.ts components/manuscript/
```

Expected: PASS.

- [ ] **Step 2: Run any nav-dependent unit tests**

```bash
cd frontend && npm test -- components/chrome/CommandPalette.test.tsx lib/nav.test.ts
```

Expected: PASS (palette derives from PRIMARY_NAV).

- [ ] **Step 3: Manual checklist (dev server)**

```bash
# from repo root, if stack is up
# open /manuscript — TOC + reader
# click section — scrolls
# Modifica — lands on /writing/<id>
# Confirm no edit controls in reader
```

- [ ] **Step 4: Do not implement Revisiona**

Leave a single code comment near the action cluster is optional; prefer **no** dead buttons. Spec §7 already records v2: `Revisiona` → `/review?chapter={id}`.

- [ ] **Step 5: Commit** (only if user requested) — verification-only; skip empty commit.

---

## Spec coverage checklist

| Spec requirement | Task |
|------------------|------|
| Sidebar Manoscritto + ADR-0036 | Task 1 |
| `/manuscript` + `/manuscript/[chapterId]` | Task 6 |
| TOC order, status, words, `#`/`##` sections | Tasks 2, 4, 6 |
| Reader rendered markdown | Tasks 3, 5 |
| Prev/Next | Tasks 5, 6 |
| Modifica → Writing only | Tasks 5, 6 |
| Empty thesis / empty chapter | Task 5 |
| Fetch contents for full section tree | Task 6 |
| No Review merge / no Revisiona in v1 | Task 7 + Global Constraints |
| Future edit-in-manuscript / Writing demotion | Documented in spec only |

## Self-review notes

- Fixed IA count language: **six** primary + Settings (not seven).
- Modifica locked to `Link href=/writing/...` for safe navigation.
- No `react-markdown` dependency — custom renderer keeps package surface small.
- Revisiona explicitly deferred; natural v2 action beside Modifica.
