import { describe, expect, it } from "vitest";
import {
  hasBlockingCitationIssues,
  suggestAuthorDate,
  validateCitations,
} from "@/lib/citationValidation";

const SOURCES = [
  { author: "Josef Albers", year: "1963" },
  { author: "Walter Benjamin", year: "1936" },
  { author: "Barney Glaser e Anselm Strauss", year: "1967" },
];

describe("citationValidation", () => {
  it("flags numeric cites", () => {
    const issues = validateCitations("Teoria [2] cromatica.", SOURCES);
    expect(issues).toHaveLength(1);
    expect(issues[0].code).toBe("invalid_numeric");
  });

  it("suggests author-date from source index", () => {
    expect(suggestAuthorDate(SOURCES, 2)).toBe("(Benjamin, 1936)");
  });

  it("blocks Applica when numeric present", () => {
    expect(hasBlockingCitationIssues("Test [1] qui.", SOURCES)).toBe(true);
  });

  it.each([
    "L’aura cambia (Benjamin, 1936).",
    "Benjamin (1936) descrive l’aura.",
    "Il metodo è iterativo (Glaser & Strauss, 1967).",
    "Il metodo è iterativo (Glaser e Strauss, 1967).",
  ])("accepts a linked author-date citation: %s", (text) => {
    expect(validateCitations(text, SOURCES)).toEqual([]);
  });

  it("blocks an author-date citation not linked to the bibliography", () => {
    const text = "Una tesi inesistente (FantomaAutore, 2050).";

    expect(validateCitations(text, SOURCES)).toEqual([
      expect.objectContaining({
        code: "unlinked_author_date",
        matched: "(FantomaAutore, 2050)",
      }),
    ]);
    expect(hasBlockingCitationIssues(text, SOURCES)).toBe(true);
  });

  it("treats an explicit empty bibliography as unlinked", () => {
    expect(validateCitations("(Benjamin, 1936)", [])[0]?.code).toBe(
      "unlinked_author_date"
    );
  });

  it("keeps omitted sources in local format-only mode", () => {
    expect(validateCitations("(FantomaAutore, 2050)")).toEqual([]);
  });
});
