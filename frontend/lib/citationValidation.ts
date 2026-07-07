/** Citation format validation (PX6-EWO-002/003) — mirrors backend rules. */

export type CitationSourceRef = {
  author?: string;
  year?: string | number;
  title?: string;
};

export type CitationIssue = {
  start: number;
  end: number;
  code: "invalid_numeric" | "needs_review" | "valid_linked";
  message: string;
  suggestion?: string;
  matched: string;
};

const AUTHOR_DATE_RE = /\([A-Za-zÀ-ÿ][\w'-]+,\s*\d{4}\)/;
const NUMERIC_CITE_RE = /\[\d+\]/g;
const LINKED_MARKER_RE = /\[@\w+\d*\]/g;

function surnameFromAuthor(author: string): string {
  const parts = author.trim().split(/\s+/);
  return parts[parts.length - 1]?.replace(/[^a-zA-ZÀ-ÿ]/g, "") || "Autore";
}

export function suggestAuthorDate(
  sources: CitationSourceRef[] | undefined,
  index?: number
): string {
  if (!sources?.length) return "(Autore, Anno)";
  const src = index != null && index >= 1 && index <= sources.length
    ? sources[index - 1]
    : sources[0];
  const author = src.author ?? "";
  const yearStr = String(src.year ?? "");
  const yearMatch = yearStr.match(/\b(19|20)\d{2}\b/);
  const year = yearMatch?.[0] ?? "n.d.";
  return `(${surnameFromAuthor(author)}, ${year})`;
}

export function validateCitations(
  text: string,
  sources?: CitationSourceRef[]
): CitationIssue[] {
  if (!text.trim()) return [];

  const issues: CitationIssue[] = [];
  const seen = new Set<string>();

  for (const match of text.matchAll(NUMERIC_CITE_RE)) {
    const matched = match[0];
    const start = match.index ?? 0;
    const key = `${start}:${matched}`;
    if (seen.has(key)) continue;
    seen.add(key);
    const idx = parseInt(matched.slice(1, -1), 10);
    issues.push({
      start,
      end: start + matched.length,
      code: "invalid_numeric",
      message: "Citazione numerica — preferire (Autore, Anno)",
      suggestion: suggestAuthorDate(sources, idx),
      matched,
    });
  }

  // Suppress issues inside author-date spans (simple heuristic)
  if (AUTHOR_DATE_RE.test(text) && issues.length === 0) {
    return [];
  }

  void LINKED_MARKER_RE;
  return issues;
}

export function hasBlockingCitationIssues(
  text: string,
  sources?: CitationSourceRef[]
): boolean {
  return validateCitations(text, sources).some((i) => i.code === "invalid_numeric");
}

export function countInvalidNumericCitations(text: string): number {
  return validateCitations(text).filter((i) => i.code === "invalid_numeric").length;
}
