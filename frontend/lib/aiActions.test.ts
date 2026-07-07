import { afterEach, describe, expect, it, vi } from "vitest";
import { streamWritingAction } from "@/lib/aiActions";
import { CONTEXT_STUB } from "@/lib/contextClient";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("Writing aiActions", () => {
  it("emits error event on 503 instead of mock stream", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue({
      ok: false,
      status: 503,
      statusText: "Service Unavailable",
      json: async () => ({
        code: "llm_not_configured",
        message: "LLM runtime not configured",
      }),
    } as Response);

    const events: string[] = [];
    await streamWritingAction(
      {
        actionId: "verify",
        chapterId: "1",
        contextPacket: CONTEXT_STUB,
      },
      (event) => {
        if (event.event === "error") {
          events.push(event.data.message);
        }
      }
    );

    expect(events).toEqual(["LLM runtime not configured"]);
  });

  it("emits error event on network failure", async () => {
    vi.spyOn(global, "fetch").mockRejectedValue(new Error("fetch failed"));

    const events: string[] = [];
    await streamWritingAction(
      {
        actionId: "rewrite",
        chapterId: "1",
        selectionText: "test",
        contextPacket: CONTEXT_STUB,
      },
      (event) => {
        if (event.event === "error") {
          events.push(event.data.code);
        }
      }
    );

    expect(events).toEqual(["network_error"]);
  });
});
