import type { ContextPacket, DecisionRef, EntityScope } from "@/lib/contextClient";

export type DecisionStatus = "vincolante" | "aperta";

/** Enriched decision view for UI — parsed from ContextPacket without backend changes. */
export type DecisionView = {
  id: string;
  displayId: string;
  title: string;
  summary: string;
  fullSummary: string;
  binding: boolean;
  frozen: boolean;
  status: DecisionStatus;
  influencedChapters: string[];
};

export const ASK_REVIEWER_EVENT = "thesisos:ask-reviewer";

export type AskReviewerDetail = {
  decisionId: string;
};

const CHAPTER_REF_RE = /Cap(?:itolo)?\.?\s*(\d+)/gi;
const DISPLAY_ID_RE =
  /\b(CORPUS-\d+|REV-\d+|METH-\d+|UNI-\d+|REL-\d+|RED-\d+|MEM-\d+|PLAT-\d+|DEC-\d+)\b/i;

export function formatDecisionDisplayId(ref: DecisionRef): string {
  if (ref.title?.trim()) {
    const title = ref.title.trim();
    if (DISPLAY_ID_RE.test(title) || /^[A-Z0-9-]+$/i.test(title)) {
      return title.toUpperCase();
    }
  }

  const fromSummary = ref.summary.match(DISPLAY_ID_RE);
  if (fromSummary) {
    return fromSummary[1].toUpperCase();
  }

  const fromId = ref.id.match(
    /(?:^|[-_])(corpus-\d+|rev-\d+|meth-\d+|uni-\d+|rel-\d+|red-\d+|mem-\d+|plat-\d+|dec-\d+)/i
  );
  if (fromId) {
    return fromId[1].toUpperCase();
  }

  return ref.id.toUpperCase();
}

export function parseInfluencedChapters(ref: DecisionRef): string[] {
  const text = `${ref.summary} ${ref.title ?? ""}`;
  const chapters = new Set<string>();

  for (const match of text.matchAll(CHAPTER_REF_RE)) {
    chapters.add(`Cap. ${match[1]}`);
  }

  const influenceMatch = text.match(/Influenza\s*:\s*([^.\n]+)/i);
  if (influenceMatch) {
    for (const match of influenceMatch[1].matchAll(CHAPTER_REF_RE)) {
      chapters.add(`Cap. ${match[1]}`);
    }
  }

  return [...chapters];
}

export function parseDecision(ref: DecisionRef): DecisionView {
  const binding = ref.binding;
  const displayId = formatDecisionDisplayId(ref);
  const title =
    ref.title && !DISPLAY_ID_RE.test(ref.title.trim())
      ? ref.title.trim()
      : ref.summary.split(/[—–-]/)[0]?.trim() || ref.summary;

  return {
    id: ref.id,
    displayId,
    title,
    summary: ref.summary,
    fullSummary: ref.summary,
    binding,
    frozen: binding,
    status: binding ? "vincolante" : "aperta",
    influencedChapters: parseInfluencedChapters(ref),
  };
}

export function parseDecisionsFromPacket(packet: ContextPacket): DecisionView[] {
  return packet.decisions.map(parseDecision);
}

export function bindingDecisionViews(decisions: DecisionView[]): DecisionView[] {
  return decisions.filter((d) => d.binding);
}

export function entityMatchesInfluencedChapter(
  entity: EntityScope,
  chapters: string[]
): boolean {
  if (chapters.length === 0) {
    return false;
  }

  const entityText = `${entity.title} ${entity.id}`.toLowerCase();
  return chapters.some((chapter) => {
    const num = chapter.match(/\d+/)?.[0];
    if (!num) {
      return false;
    }
    return (
      entity.id === num ||
      entityText.includes(`cap. ${num}`) ||
      entityText.includes(`capitolo ${num}`) ||
      entityText.includes(`cap ${num}`)
    );
  });
}

export function findConflictingDecision(
  decisions: DecisionView[],
  entity?: EntityScope | null,
  selectionText?: string | null
): DecisionView | null {
  const binding = bindingDecisionViews(decisions);
  if (binding.length === 0) {
    return null;
  }

  const hasSelection = Boolean(selectionText?.trim());

  for (const decision of binding) {
    if (
      entity &&
      hasSelection &&
      entityMatchesInfluencedChapter(entity, decision.influencedChapters) &&
      selectionTouchesDecision(selectionText!, decision)
    ) {
      return decision;
    }
  }

  if (entity?.type === "chapter" && hasSelection) {
    const globalBinding = binding.find((d) => d.influencedChapters.length === 0);
    if (globalBinding && selectionTouchesDecision(selectionText!, globalBinding)) {
      return globalBinding;
    }
  }

  return null;
}

function selectionTouchesDecision(selection: string, decision: DecisionView): boolean {
  const normalized = selection.toLowerCase();
  const rawKeywords = [
    decision.displayId,
    decision.title,
    ...decision.summary.split(/[—–,\s]+/),
  ];

  const keywords = rawKeywords
    .map((keyword) => keyword.toLowerCase().replace(/[^\p{L}\p{N}\s-]/gu, "").trim())
    .filter((keyword) => keyword.length > 3);

  return keywords.some((keyword) => normalized.includes(keyword));
}

export function topRelevantDecisions(
  decisions: DecisionView[],
  entity?: EntityScope | null,
  limit = 3
): DecisionView[] {
  const binding = bindingDecisionViews(decisions);
  const ranked = [...binding].sort((a, b) => {
    const aMatch = entity ? entityMatchesInfluencedChapter(entity, a.influencedChapters) : false;
    const bMatch = entity ? entityMatchesInfluencedChapter(entity, b.influencedChapters) : false;
    if (aMatch !== bMatch) {
      return aMatch ? -1 : 1;
    }
    return a.displayId.localeCompare(b.displayId);
  });

  return ranked.slice(0, limit);
}

export function dispatchAskReviewer(decisionId: string): void {
  if (typeof window === "undefined") {
    return;
  }
  window.dispatchEvent(
    new CustomEvent<AskReviewerDetail>(ASK_REVIEWER_EVENT, {
      detail: { decisionId },
    })
  );
}
