import type { ChapterStatus } from "@/lib/chapterClient";

/** ADR-0040 — deterministic status factors (not LLM-estimated) */
export const STATUS_FACTOR: Record<ChapterStatus, number> = {
  draft: 0.4,
  review: 0.7,
  approved: 1.0,
  published: 1.0,
};

export type ProgressChapter = {
  id: string;
  title: string;
  status: ChapterStatus;
  /** Outline metadata weight; default 1 */
  weight?: number;
};

/**
 * progress_pct = Σ (chapter_weight × status_factor) / Σ chapter_weight
 * ADR-0040 INV-PS-1
 */
export function computeProgressPct(chapters: ProgressChapter[]): number {
  if (chapters.length === 0) return 0;
  let weighted = 0;
  let totalWeight = 0;
  for (const ch of chapters) {
    const w = ch.weight ?? 1;
    weighted += w * STATUS_FACTOR[ch.status];
    totalWeight += w;
  }
  if (totalWeight === 0) return 0;
  return Math.round((weighted / totalWeight) * 100);
}

export type ContinueTarget = {
  href: string;
  label: string;
};

/** Deep link to active chapter — stub until activity log (ADR-0040) */
export function findContinueTarget(chapters: ProgressChapter[]): ContinueTarget {
  const active = chapters.find(
    (c) => c.status === "draft" || c.status === "review"
  );
  if (active) {
    return { href: `/writing/${active.id}`, label: active.title };
  }
  if (chapters.length > 0) {
    return { href: `/writing/${chapters[0].id}`, label: chapters[0].title };
  }
  return { href: "/writing", label: "Inizia a scrivere" };
}

/** Phase label stub from outline metadata — PX-1 placeholder */
export function progressPhaseLabel(pct: number): string {
  if (pct === 0) return "Prima dei dieci minuti";
  if (pct < 40) return "Struttura e impostazione";
  if (pct < 70) return "Sviluppo argomentativo";
  if (pct < 100) return "Revisione e rifinitura";
  return "Capitoli approvati";
}
