import type { ChapterStatus } from "@/lib/chapterClient";

/** PX-1 outline stub — replaced by chapters API in PX-2 */
export type WritingOutlineChapter = {
  id: string;
  title: string;
  status: ChapterStatus;
};

export const WRITING_OUTLINE_STUB: WritingOutlineChapter[] = [
  { id: "1", title: "Cap. 1 — Introduzione", status: "approved" },
  { id: "2", title: "Cap. 2 — Quadro teorico", status: "review" },
  { id: "3", title: "Cap. 3 — Metodologia", status: "draft" },
  { id: "4", title: "Cap. 4 — Analisi", status: "draft" },
  { id: "5", title: "Cap. 5 — STIGMATA", status: "draft" },
];

export const CHAPTER_STATUS_LABELS: Record<ChapterStatus, string> = {
  draft: "Bozza",
  review: "In revisione",
  approved: "Approvato",
  published: "Pubblicato",
};

export type WritingAiAction = {
  id: string;
  label: string;
  description: string;
};

/** Contextual AI actions — execution deferred to PX-2 (Spec §5.6) */
export const WRITING_AI_ACTIONS: WritingAiAction[] = [
  {
    id: "rewrite",
    label: "Riscrivi",
    description: "Riformula il paragrafo selezionato",
  },
  {
    id: "deepen",
    label: "Approfondisci",
    description: "Espandi l'argomento con fonti dal corpus",
  },
  {
    id: "find-sources",
    label: "Trova fonti",
    description: "Cerca citazioni pertinenti nel corpus",
  },
  {
    id: "verify",
    label: "Verifica",
    description: "Controlla coerenza con decisioni vincolanti",
  },
  {
    id: "compare",
    label: "Confronta",
    description: "Confronta con versioni precedenti",
  },
  {
    id: "summarize",
    label: "Riassumi",
    description: "Sintetizza la sezione corrente",
  },
];

export function chapterTitle(chapterId: string): string {
  const match = WRITING_OUTLINE_STUB.find((ch) => ch.id === chapterId);
  return match?.title ?? `Capitolo ${chapterId}`;
}
