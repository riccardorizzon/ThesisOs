/** Citation format validation (PX6-EWO-002/003) — mirrors backend rules. */

export type CitationSourceRef = {
  author?: string;
  year?: string | number;
  title?: string;
};

export type CitationIssue = {
  start: number;
  end: number;
  code:
    | "invalid_numeric"
    | "needs_review"
    | "valid_linked"
    | "unlinked_author_date";
  message: string;
  suggestion?: string;
  matched: string;
};

const PARENTHETICAL_AUTHOR_DATE_RE =
  /\(([A-ZÀ-ÖØ-Þ][^,()]{0,120}),\s*((?:19|20)\d{2}|[ns]\.?\s*d\.?)\)/gu;
const NARRATIVE_AUTHOR_DATE_RE =
  /([A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÿ'’\-]+(?:\s+(?:&|e|and)\s+[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÿ'’\-]+)*)\s*\(\s*((?:19|20)\d{2}|[ns]\.?\s*d\.?)\s*\)/gu;
const NUMERIC_CITE_RE = /\[\d+\]/g;
const LINKED_MARKER_RE = /\[@\w+\d*\]/g;
const AUTHOR_CONNECTORS = new Set(["e", "and", "et", "al"]);

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

function normalizedTokens(value: string): Set<string> {
  const tokens = value
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .match(/[a-z0-9]+/g) ?? [];
  return new Set(
    tokens.filter(
      (token) => token.length > 1 && !AUTHOR_CONNECTORS.has(token)
    )
  );
}

function normalizedYear(value: string | number | undefined): string {
  return String(value ?? "").match(/\b(19|20)\d{2}\b/)?.[0] ?? "n.d.";
}

function isLinkedAuthorDate(
  authors: string,
  year: string,
  sources: CitationSourceRef[]
): boolean {
  const citedTokens = normalizedTokens(authors);
  const citedYear = normalizedYear(year);
  if (citedTokens.size === 0) return false;
  return sources.some((source) => {
    if (normalizedYear(source.year) !== citedYear) return false;
    const sourceTokens = normalizedTokens(source.author ?? "");
    return [...citedTokens].every((token) => sourceTokens.has(token));
  });
}

type AuthorDateMatch = {
  start: number;
  end: number;
  matched: string;
  authors: string;
  year: string;
};

function authorDateMatches(text: string): AuthorDateMatch[] {
  const matches = [
    ...text.matchAll(PARENTHETICAL_AUTHOR_DATE_RE),
    ...text.matchAll(NARRATIVE_AUTHOR_DATE_RE),
  ];
  return matches
    .map((match) => ({
      start: match.index ?? 0,
      end: (match.index ?? 0) + match[0].length,
      matched: match[0],
      authors: match[1] ?? "",
      year: match[2] ?? "",
    }))
    .sort((left, right) => left.start - right.start);
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

  for (const match of text.matchAll(LINKED_MARKER_RE)) {
    const start = match.index ?? 0;
    seen.add(`${start}:${match[0]}`);
  }

  if (sources !== undefined) {
    for (const match of authorDateMatches(text)) {
      const key = `${match.start}:${match.matched}`;
      if (seen.has(key)) continue;
      seen.add(key);
      if (isLinkedAuthorDate(match.authors, match.year, sources)) continue;
      issues.push({
        start: match.start,
        end: match.end,
        code: "unlinked_author_date",
        message: "Citazione non collegata alla bibliografia del progetto",
        suggestion: "Aggiungi o collega questa fonte alla bibliografia",
        matched: match.matched,
      });
    }
  }

  return issues;
}

export function hasBlockingCitationIssues(
  text: string,
  sources?: CitationSourceRef[]
): boolean {
  return validateCitations(text, sources).some((issue) =>
    issue.code === "invalid_numeric" || issue.code === "unlinked_author_date"
  );
}

export function countInvalidNumericCitations(text: string): number {
  return validateCitations(text).filter((i) => i.code === "invalid_numeric").length;
}
