import { describe, expect, it } from "vitest";
import type { Chapter } from "./chapterClient";
import {
  buildManuscriptOutline,
  dedupeManuscriptChapters,
  flattenManuscriptOutline,
  neighborChapterIds,
  parseManuscriptTitle,
  sortChaptersByOrder,
  sortManuscriptChapters,
  stripManuscriptTag,
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

describe("parseManuscriptTitle", () => {
  it("parses section and chapter titles", () => {
    expect(parseManuscriptTitle("[tag] §3.6 Sintesi del capitolo")).toEqual({
      kind: "section",
      major: 3,
      minor: 6,
      label: "Sintesi del capitolo",
    });
    expect(parseManuscriptTitle("Cap. 3 — Progettazione metodologica")).toEqual({
      kind: "chapter",
      major: 3,
      label: "Progettazione metodologica",
    });
  });
});

describe("dedupeManuscriptChapters", () => {
  it("drops noise and keeps the richest duplicate title", () => {
    const deduped = dedupeManuscriptChapters([
      ch({ id: "noise", title: "G5 walkthrough", order_index: 0, word_count: 4 }),
      ch({
        id: "draft",
        title: "§1.1 Intro",
        order_index: 0,
        status: "draft",
        word_count: 0,
      }),
      ch({
        id: "review",
        title: "[kimi] §1.1 Intro",
        order_index: 0,
        status: "review",
        word_count: 120,
      }),
    ]);
    expect(deduped.map((c) => c.id)).toEqual(["review"]);
  });
});

describe("sortManuscriptChapters", () => {
  it("orders by major/minor not raw order_index", () => {
    const sorted = sortManuscriptChapters([
      ch({ id: "c3", title: "Cap. 3 — Metodo", order_index: 7 }),
      ch({ id: "s36", title: "§3.6 Sintesi", order_index: 36 }),
      ch({ id: "s31", title: "§3.1 Palette", order_index: 31 }),
      ch({ id: "s11", title: "§1.1 Intro", order_index: 0 }),
    ]);
    expect(sorted.map((c) => c.id)).toEqual(["s11", "c3", "s31", "s36"]);
  });
});

describe("buildManuscriptOutline", () => {
  it("builds Cap. N groups with §N.x sections", () => {
    const outline = buildManuscriptOutline([
      ch({ id: "s11", title: "§1.1 Intro", order_index: 0, status: "review", word_count: 10 }),
      ch({ id: "s12", title: "§1.2 Flow", order_index: 1, status: "review", word_count: 20 }),
      ch({
        id: "c3",
        title: "Cap. 3 — Progettazione",
        order_index: 7,
        status: "review",
        word_count: 100,
      }),
      ch({ id: "s31", title: "§3.1 Palette", order_index: 31, status: "review", word_count: 5 }),
      ch({ id: "s36", title: "§3.6 Sintesi", order_index: 36, status: "draft", word_count: 7 }),
    ]);

    expect(outline.parts.map((p) => p.number)).toEqual(["1", "3"]);
    expect(outline.parts[0]!.sections.map((s) => s.number)).toEqual(["1.1", "1.2"]);
    expect(outline.parts[1]!.title).toBe("Progettazione");
    expect(outline.parts[1]!.chapterId).toBe("c3");
    expect(outline.parts[1]!.sections.map((s) => s.number)).toEqual(["3.1", "3.6"]);
    expect(outline.parts[1]!.sections[1]!.label).toBe("Sintesi");
    expect(outline.others).toEqual([]);
  });

  it("collects free titles under others", () => {
    const outline = buildManuscriptOutline([
      ch({ id: "c1", title: "Cap. 1 — Introduzione", order_index: 0 }),
      ch({ id: "free", title: "Introduzione", order_index: 2, word_count: 5 }),
      ch({ id: "notes", title: "Appunti", order_index: 1, word_count: 3 }),
    ]);

    expect(outline.parts.map((p) => p.chapterId)).toEqual(["c1"]);
    expect(outline.others.map((o) => o.id)).toEqual(["notes", "free"]);
    expect(outline.others.map((o) => o.label)).toEqual(["Appunti", "Introduzione"]);
  });
});

describe("flattenManuscriptOutline", () => {
  it("walks chapter header then sections then others", () => {
    const outline = buildManuscriptOutline([
      ch({ id: "c3", title: "Cap. 3 — Progettazione", order_index: 7 }),
      ch({ id: "s31", title: "§3.1 Palette", order_index: 31 }),
      ch({ id: "s36", title: "§3.6 Sintesi", order_index: 36 }),
      ch({ id: "free", title: "Introduzione", order_index: 40 }),
    ]);
    expect(flattenManuscriptOutline(outline)).toEqual(["c3", "s31", "s36", "free"]);
  });
});

describe("stripManuscriptTag", () => {
  it("removes leading batch tags", () => {
    expect(stripManuscriptTag("[kimi-claw-2026-07-13] §3.6 Sintesi")).toBe("§3.6 Sintesi");
  });
});

describe("sortChaptersByOrder", () => {
  it("orders by order_index ascending", () => {
    const sorted = sortChaptersByOrder([
      ch({ id: "b", title: "B", order_index: 2 }),
      ch({ id: "a", title: "A", order_index: 0 }),
    ]);
    expect(sorted.map((c) => c.id)).toEqual(["a", "b"]);
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
  it("returns prev/next across flattened outline", () => {
    expect(neighborChapterIds(["c3", "s31", "s36"], "s31")).toEqual({
      prevId: "c3",
      nextId: "s36",
    });
  });
});
