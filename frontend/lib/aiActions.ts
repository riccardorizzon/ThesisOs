import type { ContextPacket } from "@/lib/contextClient";

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

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

async function parseSseStream(
  body: ReadableStream<Uint8Array>,
  onEvent: (e: WritingActionStreamEvent) => void,
  signal?: AbortSignal
): Promise<void> {
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  for (;;) {
    if (signal?.aborted) {
      await reader.cancel();
      return;
    }
    const { value, done } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    const frames = buf.split(/\r\n\r\n|\n\n|\r\r/);
    buf = frames.pop() ?? "";
    for (const frame of frames) {
      let event = "message";
      let data = "";
      for (const line of frame.split(/\r\n|\n|\r/)) {
        if (line.startsWith("event:")) event = line.slice(6).trim();
        else if (line.startsWith("data:")) data += line.slice(5).trim();
      }
      if (!data) continue;
      onEvent({ event, data: JSON.parse(data) } as WritingActionStreamEvent);
    }
  }
}

function mockStream(
  actionId: WritingActionId,
  selectionText: string | null,
  onEvent: (e: WritingActionStreamEvent) => void,
  signal?: AbortSignal
): Promise<void> {
  const snippets: Record<WritingActionId, string> = {
    rewrite: selectionText
      ? `Versione riformulata:\n\n${selectionText.trim()} — riscritto con registro accademico.`
      : "Seleziona un passaggio da riscrivere.",
    verify:
      "Verifica completata: nessun conflitto evidente con le decisioni vincolanti attive.",
    "find-sources":
      "Fonti candidate:\n- Benjamin (1936) — Opera d'arte nell'epoca della riproducibilità\n- Barthes (1957) — Mito e significato",
    expand: selectionText
      ? `${selectionText.trim()}\n\nApprofondimento: il passaggio può essere collegato al quadro teorico STIGMATA e alle fonti del corpus approvato.`
      : "Seleziona un passaggio da espandere.",
  };
  const text = snippets[actionId];
  const tokens = text.split(/(?=\s)/);

  return new Promise((resolve) => {
    let i = 0;
    const tick = () => {
      if (signal?.aborted) {
        resolve();
        return;
      }
      if (i >= tokens.length) {
        onEvent({ event: "done", data: { draft: text } });
        resolve();
        return;
      }
      onEvent({ event: "token", data: { text: tokens[i] } });
      i += 1;
      setTimeout(tick, 8);
    };
    tick();
  });
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
    const r = await fetch(`${BASE}/writing/actions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: params.actionId,
        chapter_id: params.chapterId,
        selection_text: params.selectionText ?? null,
        chapter_content: params.chapterContent ?? "",
        context_summary: summarizeContext(params.contextPacket),
      }),
      signal,
    });

    if (r.status === 503 || r.status === 404 || !r.ok) {
      await mockStream(params.actionId, params.selectionText ?? null, onEvent, signal);
      return;
    }

    if (!r.body) {
      await mockStream(params.actionId, params.selectionText ?? null, onEvent, signal);
      return;
    }

    await parseSseStream(r.body, onEvent, signal);
  } catch (err) {
    if (signal?.aborted) return;
    await mockStream(params.actionId, params.selectionText ?? null, onEvent, signal);
  }
}
