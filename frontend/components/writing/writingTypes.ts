import type { ChapterStatus } from "@/lib/chapterClient";

export type WritingOutlineChapter = {
  id: string;
  title: string;
  status: ChapterStatus;
  version: number;
};

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
