import { describe, expect, it } from "vitest";
import {
  hasBlockingCitationIssues,
  suggestAuthorDate,
  validateCitations,
} from "@/lib/citationValidation";

const SOURCES = [
  { author: "Josef Albers", year: "1963" },
  { author: "Walter Benjamin", year: "1936" },
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
});
