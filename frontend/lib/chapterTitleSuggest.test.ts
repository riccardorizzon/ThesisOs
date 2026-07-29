import { describe, expect, it } from "vitest";
import {
  formatChapterTitle,
  suggestChapterTitle,
  type ChapterTitleKind,
} from "@/lib/chapterTitleSuggest";

describe("formatChapterTitle", () => {
  it("formats chapter and section titles", () => {
    expect(formatChapterTitle("chapter", 2, undefined, "Metodo")).toBe(
      "Cap. 2 — Metodo"
    );
    expect(formatChapterTitle("section", 1, 3, "Palette")).toBe("§1.3 Palette");
    expect(formatChapterTitle("free", 0, undefined, "Introduzione")).toBe(
      "Introduzione"
    );
  });
});

describe("suggestChapterTitle", () => {
  const chapters = [
    { title: "Cap. 1 — Introduzione" },
    { title: "§1.1 Contesto" },
    { title: "§1.2 Domanda" },
    { title: "Cap. 2 — Quadro" },
  ];

  it("suggests next chapter major", () => {
    expect(suggestChapterTitle(chapters, "chapter")).toBe(
      "Cap. 3 — Nuovo capitolo"
    );
  });

  it("suggests next section under latest major", () => {
    expect(suggestChapterTitle(chapters, "section")).toBe(
      "§2.1 Titolo sezione"
    );
  });

  it("suggests Introduzione for free", () => {
    expect(suggestChapterTitle(chapters, "free")).toBe("Introduzione");
  });

  it("starts at Cap. 1 and §1.1 when empty", () => {
    expect(suggestChapterTitle([], "chapter")).toBe("Cap. 1 — Nuovo capitolo");
    expect(suggestChapterTitle([], "section")).toBe("§1.1 Titolo sezione");
  });

  it("accepts all kinds", () => {
    const kinds: ChapterTitleKind[] = ["chapter", "section", "free"];
    for (const kind of kinds) {
      expect(suggestChapterTitle([], kind).length).toBeGreaterThan(0);
    }
  });
});
