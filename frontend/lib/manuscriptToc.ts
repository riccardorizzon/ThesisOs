import type { Chapter } from "@/lib/chapterClient";
import { parseMarkdownSections } from "@/components/writing/MarkdownEditor";

export type ManuscriptTocSection = {
  id: string;
  label: string;
  level: number;
};

export type ManuscriptTocChapter = {
  id: string;
  title: string;
  status: Chapter["status"];
  word_count: number;
  order_index: number;
  sections: ManuscriptTocSection[];
};

export function sortChaptersByOrder(chapters: Chapter[]): Chapter[] {
  return [...chapters].sort((a, b) => a.order_index - b.order_index);
}

export function buildManuscriptToc(chapters: Chapter[]): ManuscriptTocChapter[] {
  return sortChaptersByOrder(chapters).map((chapter) => {
    const sections = parseMarkdownSections(chapter.content_md ?? "").map((s) => ({
      id: s.id,
      label: s.label,
      level: s.level,
    }));
    return {
      id: chapter.id,
      title: chapter.title,
      status: chapter.status,
      word_count: chapter.word_count,
      order_index: chapter.order_index,
      sections,
    };
  });
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
