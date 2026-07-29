import { parseManuscriptTitle } from "@/lib/manuscriptToc";

export type ChapterTitleKind = "chapter" | "section" | "free";

export function formatChapterTitle(
  kind: ChapterTitleKind,
  major: number,
  minor: number | undefined,
  label: string
): string {
  const trimmed = label.trim() || (kind === "section" ? "Titolo sezione" : "Nuovo capitolo");
  if (kind === "chapter") {
    return `Cap. ${major} — ${trimmed}`;
  }
  if (kind === "section") {
    return `§${major}.${minor ?? 1} ${trimmed}`;
  }
  return trimmed;
}

function scanMajors(chapters: { title: string }[]): {
  maxChapterMajor: number;
  maxSectionByMajor: Map<number, number>;
  latestMajor: number;
} {
  let maxChapterMajor = 0;
  let latestMajor = 0;
  const maxSectionByMajor = new Map<number, number>();

  for (const chapter of chapters) {
    const parsed = parseManuscriptTitle(chapter.title);
    if (parsed.kind === "chapter") {
      maxChapterMajor = Math.max(maxChapterMajor, parsed.major);
      latestMajor = Math.max(latestMajor, parsed.major);
    } else if (parsed.kind === "section") {
      latestMajor = Math.max(latestMajor, parsed.major);
      const prev = maxSectionByMajor.get(parsed.major) ?? 0;
      maxSectionByMajor.set(parsed.major, Math.max(prev, parsed.minor));
    }
  }

  return { maxChapterMajor, maxSectionByMajor, latestMajor };
}

/**
 * Suggest a Cap./§/free title based on existing chapter titles.
 */
export function suggestChapterTitle(
  chapters: { title: string }[],
  kind: ChapterTitleKind
): string {
  if (kind === "free") {
    return "Introduzione";
  }

  const { maxChapterMajor, maxSectionByMajor, latestMajor } = scanMajors(chapters);

  if (kind === "chapter") {
    return formatChapterTitle("chapter", maxChapterMajor + 1, undefined, "Nuovo capitolo");
  }

  const major = latestMajor > 0 ? latestMajor : 1;
  const nextMinor = (maxSectionByMajor.get(major) ?? 0) + 1;
  return formatChapterTitle("section", major, nextMinor, "Titolo sezione");
}
