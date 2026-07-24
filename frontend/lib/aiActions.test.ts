import { afterEach, describe, expect, it, vi } from "vitest";
import { streamWritingAction } from "@/lib/aiActions";
import { FIXTURE_CONTEXT_PACKET } from "@/lib/fixtures/contextFixture";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("Writing aiActions", () => {
  it("emits a product-safe error event on 503 instead of backend copy", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          code: "llm_not_configured",
          message: "LLM runtime not configured",
        }),
        {
          status: 503,
          statusText: "Service Unavailable",
          headers: { "Content-Type": "application/json" },
        }
      )
    );

    const events: string[] = [];
    await streamWritingAction(
      {
        actionId: "verify",
        chapterId: "1",
        contextPacket: FIXTURE_CONTEXT_PACKET,
      },
      (event) => {
        if (event.event === "error") {
          events.push(event.data.message);
        }
      }
    );

    expect(events).toEqual(["L’assistente non è configurato."]);
  });

  it("emits error event on network failure", async () => {
    vi.spyOn(global, "fetch").mockRejectedValue(new Error("fetch failed"));

    const events: string[] = [];
    await streamWritingAction(
      {
        actionId: "rewrite",
        chapterId: "1",
        selectionText: "test",
        contextPacket: FIXTURE_CONTEXT_PACKET,
      },
      (event) => {
        if (event.event === "error") {
          events.push(event.data.code);
        }
      }
    );

    expect(events).toEqual(["network_error"]);
  });

  it("rejects a successful response that is not SSE", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ draft: "not streamed" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      })
    );

    const events: string[] = [];
    await streamWritingAction(
      {
        actionId: "verify",
        chapterId: "1",
        chapterContent: "Capitolo",
        contextPacket: FIXTURE_CONTEXT_PACKET,
      },
      (event) => {
        if (event.event === "error") events.push(event.data.code);
      }
    );

    expect(events).toEqual(["invalid_response"]);
  });

  it("reports a stream that ends without a terminal event", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(
      new Response('event: token\ndata: {"text":"Parziale"}\n\n', {
        status: 200,
        headers: { "Content-Type": "text/event-stream" },
      })
    );

    const events: string[] = [];
    await streamWritingAction(
      {
        actionId: "verify",
        chapterId: "1",
        chapterContent: "Capitolo",
        contextPacket: FIXTURE_CONTEXT_PACKET,
      },
      (event) => {
        if (event.event === "error") events.push(event.data.code);
      }
    );

    expect(events).toEqual(["stream_interrupted"]);
  });
});
