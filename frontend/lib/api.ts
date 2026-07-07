const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function getHealth(): Promise<{ status: string }> {
  const r = await fetch(`${BASE}/health`, { cache: "no-store" });
  if (!r.ok) throw new Error(`health ${r.status}`);
  return r.json();
}

export type ChatEvent =
  | { event: "token"; data: { text: string } }
  | { event: "ping"; data: Record<string, never> }
  | { event: "done"; data: { conversation_id: string; message_id: string; usage: unknown } }
  | { event: "error"; data: { code: string; message: string } };

export async function postChatStream(
  body: { message: string; conversation_id?: string; project_id?: string },
  onEvent: (e: ChatEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const r = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });
  if (r.status === 409) { onEvent({ event: "error", data: { code: "conversation_busy", message: "Busy" } }); return; }
  if (r.status === 503) { onEvent({ event: "error", data: { code: "llm_not_configured", message: "LLM runtime not configured" } }); return; }
  if (!r.body) throw new Error(`chat ${r.status}`);

  const reader = r.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    // SSE frames are blank-line separated; the spec allows CRLF, LF, or CR
    // terminators. sse-starlette emits CRLF, so split on all variants.
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
      onEvent({ event, data: JSON.parse(data) } as ChatEvent);
    }
  }
}
