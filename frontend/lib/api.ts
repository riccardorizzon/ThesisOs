import { apiBaseUrl } from "@/lib/apiBase";
import {
  consumeSse,
  isAbortError,
  requireSseResponse,
  SseTransportError,
} from "@/lib/sseClient";

export type ChatSource = {
  index: number;
  chunk_id: string;
  document_id: string;
  document_title: string | null;
  page_from: number | null;
  score: number;
};

export async function getHealth(): Promise<{ status: string }> {
  const r = await fetch(`${apiBaseUrl()}/health`, { cache: "no-store" });
  if (!r.ok) throw new Error(`health ${r.status}`);
  return r.json();
}

export type ChatEvent =
  | { event: "token"; data: { text: string } }
  | { event: "replace"; data: { text: string } }
  | { event: "sources"; data: { sources: ChatSource[] } }
  | { event: "ping"; data: Record<string, never> }
  | { event: "done"; data: { conversation_id: string; message_id: string; usage: unknown } }
  | { event: "error"; data: { code: string; message: string } };

const CHAT_STATUS_MESSAGES: Readonly<Record<number, string>> = {
  409: "È già in corso una risposta in questa conversazione.",
  422: "Il messaggio non è valido o è troppo lungo.",
  503: "L’assistente non è configurato.",
};

export async function postChatStream(
  body: { message: string; conversation_id?: string; project_id?: string },
  onEvent: (e: ChatEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  try {
    const response = await fetch(`${apiBaseUrl()}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal,
    });
    await requireSseResponse(response, CHAT_STATUS_MESSAGES);
    await consumeSse(
      response,
      (frame) => onEvent(frame as ChatEvent),
      signal
    );
  } catch (error) {
    if (isAbortError(error)) throw error;
    if (error instanceof SseTransportError) {
      onEvent({
        event: "error",
        data: { code: error.code, message: error.message },
      });
      return;
    }
    onEvent({
      event: "error",
      data: {
        code: "network_error",
        message: "Connessione all’assistente non disponibile. Riprova.",
      },
    });
  }
}
