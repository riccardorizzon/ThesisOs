import type { Chapter, ChapterStatus } from "@/lib/chapterClient";

export type ManuscriptOutlineSection = {
  id: string;
  number: string;
  label: string;
  status: ChapterStatus;
  word_count: number;
  order_index: number;
};

export type ManuscriptOutlinePart = {
  number: string;
  title: string;
  chapterId: string | null;
  status: ChapterStatus | null;
  word_count: number;
  sections: ManuscriptOutlineSection[];
};

const TAG_PREFIX_RE = /^\[[^\]]+\]\s*/;
const SECTION_TITLE_RE = /^§\s*(\d+)\.(\d+)\s*(.+)$/;
const CHAPTER_TITLE_RE = /^Cap\.?\s*(\d+)\s*[—–-]\s*(.+)$/i;
const NOISE_TITLE_RE = /^(G5 |E2E |M7 dogfood|prova$|Craftsmanship$)/i;

export type ParsedManuscriptTitle =
  | { kind: "section"; major: number; minor: number; label: string }
  | { kind: "chapter"; major: number; label: string }
  | { kind: "other"; label: string };

export function stripManuscriptTag(title: string): string {
  return title.replace(TAG_PREFIX_RE, "").trim();
}

export function parseManuscriptTitle(title: string): ParsedManuscriptTitle {
  const stripped = stripManuscriptTag(title);
  const sectionMatch = stripped.match(SECTION_TITLE_RE);
  if (sectionMatch) {
    return {
      kind: "section",
      major: Number(sectionMatch[1]),
      minor: Number(sectionMatch[2]),
      label: sectionMatch[3]!.trim(),
    };
  }
  const chapterMatch = stripped.match(CHAPTER_TITLE_RE);
  if (chapterMatch) {
    return {
      kind: "chapter",
      major: Number(chapterMatch[1]),
      label: chapterMatch[2]!.trim(),
    };
  }
  return { kind: "other", label: stripped };
}

export function isManuscriptNoiseTitle(title: string): boolean {
  return NOISE_TITLE_RE.test(stripManuscriptTag(title));
}

export function sortChaptersByOrder(chapters: Chapter[]): Chapter[] {
  return [...chapters].sort((a, b) => a.order_index - b.order_index);
}

/** Prefer the entry with content when titles duplicate (draft stub vs review body). */
export function dedupeManuscriptChapters(chapters: Chapter[]): Chapter[] {
  const byTitle = new Map<string, Chapter>();
  for (const chapter of chapters) {
    if (isManuscriptNoiseTitle(chapter.title)) continue;
    const key = stripManuscriptTag(chapter.title).toLowerCase();
    const existing = byTitle.get(key);
    if (!existing || chapter.word_count > existing.word_count) {
      byTitle.set(key, chapter);
    }
  }
  return [...byTitle.values()];
}

function manuscriptSortTuple(chapter: Chapter): [number, number, number] {
  const parsed = parseManuscriptTitle(chapter.title);
  if (parsed.kind === "chapter") return [parsed.major, 0, 0];
  if (parsed.kind === "section") return [parsed.major, parsed.minor, 1];
  return [10_000, chapter.order_index, 2];
}

export function sortManuscriptChapters(chapters: Chapter[]): Chapter[] {
  return [...chapters].sort((a, b) => {
    const left = manuscriptSortTuple(a);
    const right = manuscriptSortTuple(b);
    for (let i = 0; i < left.length; i += 1) {
      if (left[i]! !== right[i]!) return left[i]! - right[i]!;
    }
    return 0;
  });
}

export function buildManuscriptOutline(chapters: Chapter[]): ManuscriptOutlinePart[] {
  const entries = sortManuscriptChapters(dedupeManuscriptChapters(chapters));
  const parts = new Map<number, ManuscriptOutlinePart>();

  const ensurePart = (major: number): ManuscriptOutlinePart => {
    const existing = parts.get(major);
    if (existing) return existing;
    const created: ManuscriptOutlinePart = {
      number: String(major),
      title: `Capitolo ${major}`,
      chapterId: null,
      status: null,
      word_count: 0,
      sections: [],
    };
    parts.set(major, created);
    return created;
  };

  for (const chapter of entries) {
    const parsed = parseManuscriptTitle(chapter.title);
    if (parsed.kind === "chapter") {
      const part = ensurePart(parsed.major);
      part.title = parsed.label;
      part.chapterId = chapter.id;
      part.status = chapter.status;
      part.word_count = chapter.word_count;
      continue;
    }
    if (parsed.kind === "section") {
      const part = ensurePart(parsed.major);
      part.sections.push({
        id: chapter.id,
        number: `${parsed.major}.${parsed.minor}`,
        label: parsed.label,
        status: chapter.status,
        word_count: chapter.word_count,
        order_index: chapter.order_index,
      });
    }
  }

  return [...parts.values()].sort(
    (a, b) => Number(a.number) - Number(b.number)
  );
}

/** Flat navigable chapter ids in reading order (Cap. N then §N.x). */
export function flattenManuscriptOutline(outline: ManuscriptOutlinePart[]): string[] {
  const ids: string[] = [];
  for (const part of outline) {
    if (part.chapterId) ids.push(part.chapterId);
    for (const section of part.sections) {
      ids.push(section.id);
    }
  }
  return ids;
}

export function totalWordCount(chapters: Chapter[]): number {
  return chapters.reduce((sum, c) => sum + (c.word_count ?? 0), 0);
}

export function neighborChapterIds(
  orderedIds: string[],
  currentId: string
): { prevId: string | null; nextId: string | null } {
  const index = orderedIds.indexOf(currentId);
  if (index < 0) return { prevId: null, nextId: null };
  return {
    prevId: index > 0 ? orderedIds[index - 1]! : null,
    nextId: index < orderedIds.length - 1 ? orderedIds[index + 1]! : null,
  };
}
