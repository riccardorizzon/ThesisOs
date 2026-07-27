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
