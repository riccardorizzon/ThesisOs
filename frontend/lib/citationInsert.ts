import type { SourceStatus } from "@/lib/libraryTypes";

export const INSERT_CITATION_EVENT = "thesisos:insert-citation";

export type InsertCitationDetail = {
  marker: string;
  sourceId: string;
  quote?: string;
};

/** Italian operator copy — spec §19 / IR-4 */
export const EXCLUDED_CITE_BLOCKED_MESSAGE =
  "Fonte esclusa dal corpus — non può essere citata.";

export function canCiteSource(status: SourceStatus): boolean {
  return status !== "esclusa";
}

/**
 * Project citation format: [@AuthorYear] per spec §7.4.
 */
export function formatCitationMarker(source: {
  subtitle?: string;
  meta?: string;
}): string {
  const authorPart =
    source.subtitle?.trim().split(/\s+/).pop()?.replace(/[^a-zA-ZÀ-ÿ]/g, "") ??
    "Autore";
  const yearMatch = source.meta?.match(/\b(19|20)\d{2}\b/);
  const year = yearMatch?.[0] ?? "n.d.";
  return `[@${authorPart}${year}]`;
}

export function dispatchInsertCitation(detail: InsertCitationDetail): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(
    new CustomEvent(INSERT_CITATION_EVENT, { detail })
  );
}
