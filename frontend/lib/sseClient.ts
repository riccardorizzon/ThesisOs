export type SseFrame = {
  event: string;
  data: unknown;
};

export class SseTransportError extends Error {
  readonly code: string;
  readonly status: number | null;

  constructor(code: string, message: string, status: number | null = null) {
    super(message);
    this.name = "SseTransportError";
    this.code = code;
    this.status = status;
  }
}

type ErrorBody = {
  code?: string;
};

export function isAbortError(error: unknown): boolean {
  return (
    error instanceof DOMException && error.name === "AbortError"
  ) || (
    error instanceof Error && error.name === "AbortError"
  );
}

export async function requireSseResponse(
  response: Response,
  statusMessages: Readonly<Record<number, string>> = {}
): Promise<Response> {
  if (!response.ok) {
    const contentType = response.headers.get("content-type") ?? "";
    const body = contentType.toLowerCase().includes("application/json")
      ? ((await response.clone().json().catch(() => null)) as ErrorBody | null)
      : null;
    throw new SseTransportError(
      body?.code ?? "request_failed",
      statusMessages[response.status] ?? "Servizio non disponibile. Riprova.",
      response.status
    );
  }

  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.toLowerCase().includes("text/event-stream")) {
    throw new SseTransportError(
      "invalid_response",
      "Risposta del servizio non valida. Riprova.",
      response.status
    );
  }
  if (!response.body) {
    throw new SseTransportError(
      "empty_response",
      "Il servizio non ha restituito una risposta. Riprova.",
      response.status
    );
  }
  return response;
}

function decodeFrame(frame: string): SseFrame | null {
  let event = "message";
  let data = "";
  for (const line of frame.split(/\r\n|\n|\r/)) {
    if (line.startsWith("event:")) {
      event = line.slice(6).trim();
    } else if (line.startsWith("data:")) {
      data += line.slice(5).trim();
    }
  }
  if (!data) return null;

  try {
    return { event, data: JSON.parse(data) };
  } catch {
    throw new SseTransportError(
      "invalid_response",
      "Risposta del servizio non valida. Riprova."
    );
  }
}

export async function consumeSse(
  response: Response,
  onFrame: (frame: SseFrame) => void,
  signal?: AbortSignal
): Promise<void> {
  if (!response.body) {
    throw new SseTransportError(
      "empty_response",
      "Il servizio non ha restituito una risposta. Riprova."
    );
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let terminal = false;

  const emit = (rawFrame: string) => {
    const frame = decodeFrame(rawFrame);
    if (!frame) return;
    onFrame(frame);
    if (frame.event === "done" || frame.event === "error") {
      terminal = true;
    }
  };

  for (;;) {
    if (signal?.aborted) {
      await reader.cancel();
      throw new DOMException("Aborted", "AbortError");
    }
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const frames = buffer.split(/\r\n\r\n|\n\n|\r\r/);
    buffer = frames.pop() ?? "";
    for (const frame of frames) emit(frame);
  }

  buffer += decoder.decode();
  if (buffer.trim()) emit(buffer);

  if (!terminal) {
    throw new SseTransportError(
      "stream_interrupted",
      "Risposta interrotta. Riprova."
    );
  }
}
