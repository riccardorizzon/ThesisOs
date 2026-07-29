import type { ContextPacket } from "@/lib/contextClient";
import { apiAuthHeaders } from "@/lib/apiAuth";
import { apiBaseUrl } from "@/lib/apiBase";
import { activeProjectScope } from "@/lib/projectScope";
import {
  consumeSse,
  isAbortError,
  requireSseResponse,
  SseTransportError,
} from "@/lib/sseClient";

export type WritingActionId = "rewrite" | "verify" | "find-sources" | "expand";

export type WritingActionDef = {
  id: WritingActionId;
  label: string;
  description: string;
  /** Minimum scope required */
  requiresSelection: boolean;
  allowsChapterScope: boolean;
};

export const WRITING_ACTION_DEFS: WritingActionDef[] = [
  {
    id: "rewrite",
    label: "Riscrivi",
    description: "Riformula il passaggio selezionato",
    requiresSelection: true,
    allowsChapterScope: false,
  },
  {
    id: "verify",
    label: "Verifica",
    description: "Controlla coerenza con decisioni vincolanti",
    requiresSelection: false,
    allowsChapterScope: true,
  },
  {
    id: "find-sources",
    label: "Trova fonti",
    description: "Cerca citazioni pertinenti nel corpus",
    requiresSelection: false,
    allowsChapterScope: true,
  },
  {
    id: "expand",
    label: "Espandi",
    description: "Approfondisci il passaggio con fonti dal corpus",
    requiresSelection: true,
    allowsChapterScope: false,
  },
];

export type ActionAvailability = WritingActionDef & {
  enabled: boolean;
  disabledReason: string | null;
};

export function resolveActionAvailability(
  action: WritingActionDef,
  selectionText: string | null | undefined,
  chapterContent: string | null | undefined
): ActionAvailability {
  const hasSelection = Boolean(selectionText?.trim());
  const hasChapter = Boolean(chapterContent?.trim());

  if (action.requiresSelection && !hasSelection) {
    return {
      ...action,
      enabled: false,
      disabledReason: "Seleziona un passaggio nel capitolo",
    };
  }

  if (!action.requiresSelection && !action.allowsChapterScope) {
    return { ...action, enabled: true, disabledReason: null };
  }

  if (!action.requiresSelection && action.allowsChapterScope && !hasSelection && !hasChapter) {
    return {
      ...action,
      enabled: false,
      disabledReason: "Apri un capitolo con contenuto",
    };
  }

  return { ...action, enabled: true, disabledReason: null };
}

export function getAvailableActions(
  selectionText?: string | null,
  chapterContent?: string | null
): ActionAvailability[] {
  return WRITING_ACTION_DEFS.map((action) =>
    resolveActionAvailability(action, selectionText, chapterContent)
  );
}

export type WritingActionStreamEvent =
  | { event: "token"; data: { text: string } }
  | { event: "done"; data: { draft: string } }
  | { event: "error"; data: { code: string; message: string } };

const WRITING_STATUS_MESSAGES: Readonly<Record<number, string>> = {
  400: "Azione di scrittura non valida.",
  422: "Il testo selezionato non è valido.",
  503: "L’assistente non è configurato.",
};

function summarizeContext(packet: ContextPacket): string {
  const parts: string[] = [];
  if (packet.decisions.length) {
    parts.push(
      "Decisioni vincolanti:\n" +
        packet.decisions
          .filter((d) => d.binding)
          .map((d) => `- ${d.title ?? d.id}: ${d.summary}`)
          .join("\n")
    );
  }
  if (packet.corpus_constraints.length) {
    parts.push("Vincoli corpus:\n" + packet.corpus_constraints.map((c) => `- ${c}`).join("\n"));
  }
  if (packet.writing_rules.length) {
    parts.push("Regole di scrittura:\n" + packet.writing_rules.map((r) => `- ${r}`).join("\n"));
  }
  return parts.join("\n\n");
}

function emitError(
  onEvent: (e: WritingActionStreamEvent) => void,
  code: string,
  message: string
): void {
  onEvent({ event: "error", data: { code, message } });
}

export async function streamWritingAction(
  params: {
    actionId: WritingActionId;
    chapterId: string;
    selectionText?: string | null;
    chapterContent?: string | null;
    contextPacket: ContextPacket;
  },
  onEvent: (e: WritingActionStreamEvent) => void,
  signal?: AbortSignal
): Promise<void> {
  try {
    const response = await fetch(`${apiBaseUrl()}/writing/actions`, {
      method: "POST",
      headers: apiAuthHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify({
        action: params.actionId,
        project_id: activeProjectScope(),
        chapter_id: params.chapterId,
        selection_text: params.selectionText ?? null,
        chapter_content: params.chapterContent ?? "",
        context_summary: summarizeContext(params.contextPacket),
      }),
      signal,
    });

    await requireSseResponse(response, WRITING_STATUS_MESSAGES);
    await consumeSse(
      response,
      (frame) => onEvent(frame as WritingActionStreamEvent),
      signal
    );
  } catch (err) {
    if (signal?.aborted || isAbortError(err)) return;
    if (err instanceof SseTransportError) {
      emitError(onEvent, err.code, err.message);
      return;
    }
    emitError(
      onEvent,
      "network_error",
      "Connessione al servizio AI non disponibile. Riprova."
    );
  }
}
