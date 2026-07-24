import { afterEach, describe, expect, it, vi } from "vitest";

import { postChatStream, type ChatEvent } from "@/lib/api";

afterEach(() => {
  vi.restoreAllMocks();
});

function sseResponse(body: string): Response {
  return new Response(body, {
    status: 200,
    headers: { "Content-Type": "text/event-stream; charset=utf-8" },
  });
}

describe("postChatStream transport contract", () => {
  it("emits a product error for an HTML 405 response", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(
      new Response("<!DOCTYPE html><h1>Method Not Allowed</h1>", {
        status: 405,
        headers: { "Content-Type": "text/html" },
      })
    );
    const events: ChatEvent[] = [];

    await postChatStream({ message: "Ciao" }, (event) => events.push(event));

    expect(events).toEqual([
      {
        event: "error",
        data: {
          code: "request_failed",
          message: "Servizio non disponibile. Riprova.",
        },
      },
    ]);
  });

  it("rejects a successful response that is not SSE", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      })
    );
    const events: ChatEvent[] = [];

    await postChatStream({ message: "Ciao" }, (event) => events.push(event));

    expect(events).toEqual([
      {
        event: "error",
        data: {
          code: "invalid_response",
          message: "Risposta del servizio non valida. Riprova.",
        },
      },
    ]);
  });

  it("parses CRLF events and requires a terminal frame", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(
      sseResponse(
        'event: token\r\ndata: {"text":"Ciao"}\r\n\r\n' +
          'event: done\r\ndata: {"conversation_id":"c1","message_id":"m1","usage":{}}\r\n\r\n'
      )
    );
    const events: ChatEvent[] = [];

    await postChatStream({ message: "Ciao" }, (event) => events.push(event));

    expect(events.map((event) => event.event)).toEqual(["token", "done"]);
  });

  it("emits an interruption error when a stream ends without done or error", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(
      sseResponse('event: token\ndata: {"text":"Parziale"}\n\n')
    );
    const events: ChatEvent[] = [];

    await postChatStream({ message: "Ciao" }, (event) => events.push(event));

    expect(events.at(-1)).toEqual({
      event: "error",
      data: {
        code: "stream_interrupted",
        message: "Risposta interrotta. Riprova.",
      },
    });
  });

  it("preserves AbortError as cancellation", async () => {
    const abortError = new DOMException("Aborted", "AbortError");
    vi.spyOn(global, "fetch").mockRejectedValue(abortError);

    await expect(
      postChatStream({ message: "Ciao" }, () => undefined)
    ).rejects.toBe(abortError);
  });
});
