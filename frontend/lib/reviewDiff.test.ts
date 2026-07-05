import { describe, expect, it } from "vitest";
import {
  applyProposalToContent,
  computeParagraphDiff,
  mergeAcceptedHunks,
  selectableHunks,
  splitParagraphs,
  allChangeHunkIds,
} from "@/lib/reviewDiff";

describe("splitParagraphs", () => {
  it("splits on blank lines", () => {
    expect(splitParagraphs("Primo.\n\nSecondo.\n\nTerzo.")).toEqual([
      "Primo.",
      "Secondo.",
      "Terzo.",
    ]);
  });

  it("returns empty for whitespace-only", () => {
    expect(splitParagraphs("   \n  ")).toEqual([]);
  });
});

describe("applyProposalToContent", () => {
  it("replaces selection when matched", () => {
    const original = "Intro.\n\nPassaggio vecchio.\n\nConclusione.";
    const result = applyProposalToContent(original, {
      selectionText: "Passaggio vecchio.",
      preview: "Passaggio nuovo.",
    });
    expect(result).toContain("Passaggio nuovo.");
    expect(result).not.toContain("Passaggio vecchio.");
  });

  it("uses preview as full draft when no selection match", () => {
    const result = applyProposalToContent("Vecchio contenuto.", {
      selectionText: null,
      preview: "Nuovo capitolo intero.",
    });
    expect(result).toBe("Nuovo capitolo intero.");
  });
});

describe("computeParagraphDiff", () => {
  it("marks unchanged paragraphs", () => {
    const hunks = computeParagraphDiff("A.\n\nB.", "A.\n\nB.");
    expect(hunks.every((h) => h.status === "unchanged")).toBe(true);
  });

  it("detects modified paragraph", () => {
    const hunks = computeParagraphDiff("Primo paragrafo.", "Primo paragrafo rivisto.");
    const modified = hunks.filter((h) => h.status === "modified");
    expect(modified.length).toBe(1);
    expect(modified[0].original).toBe("Primo paragrafo.");
    expect(modified[0].proposed).toBe("Primo paragrafo rivisto.");
  });

  it("detects added and removed paragraphs", () => {
    const hunks = computeParagraphDiff("Solo originale.", "Solo originale.\n\nNuovo blocco.");
    expect(hunks.some((h) => h.status === "added")).toBe(true);
  });
});

describe("mergeAcceptedHunks", () => {
  it("merges only accepted modified hunks", () => {
    const hunks = computeParagraphDiff(
      "Alpha.\n\nBeta vecchio.\n\nGamma.",
      "Alpha.\n\nBeta nuovo.\n\nGamma."
    );
    const changeIds = allChangeHunkIds(hunks);
    const accepted = new Set([...changeIds]);
    const merged = mergeAcceptedHunks(hunks, accepted);
    expect(merged).toContain("Beta nuovo.");
    expect(merged).not.toContain("Beta vecchio.");
    expect(merged).toContain("Alpha.");
    expect(merged).toContain("Gamma.");
  });

  it("keeps original when hunk not accepted", () => {
    const hunks = computeParagraphDiff("Vecchio.", "Nuovo.");
    const merged = mergeAcceptedHunks(hunks, new Set());
    expect(merged).toBe("Vecchio.");
  });
});

describe("selectableHunks", () => {
  it("excludes unchanged hunks", () => {
    const hunks = computeParagraphDiff("A.", "B.");
    expect(selectableHunks(hunks).every((h) => h.status !== "unchanged")).toBe(true);
  });
});
