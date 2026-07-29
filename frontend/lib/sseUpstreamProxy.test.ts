import { afterEach, describe, expect, it, vi } from "vitest";

import { proxySsePost } from "@/lib/sseUpstreamProxy";

afterEach(() => {
  vi.unstubAllGlobals();
  vi.unstubAllEnvs();
});

describe("proxySsePost", () => {
  it("forwards the body and streams upstream SSE without buffering headers", async () => {
    vi.stubEnv("INTERNAL_API_BASE_URL", "http://backend:8000");

    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode("event: step\ndata: {}\n\n"));
        controller.enqueue(encoder.encode("event: done\ndata: {\"draft\":\"ok\"}\n\n"));
        controller.close();
      },
    });

    const fetchMock = vi.fn().mockResolvedValue(
      new Response(stream, {
        status: 200,
        headers: { "Content-Type": "text/event-stream" },
      })
    );
    vi.stubGlobal("fetch", fetchMock);

    const request = new Request("http://localhost/api/writing/actions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "verify", chapter_content: "x" }),
    });

    const response = await proxySsePost(request, "writing/actions");

    expect(fetchMock).toHaveBeenCalledWith(
      "http://backend:8000/writing/actions",
      expect.objectContaining({
        method: "POST",
        cache: "no-store",
      })
    );
    expect(response.status).toBe(200);
    expect(response.headers.get("Content-Type")).toContain("text/event-stream");
    expect(response.headers.get("Cache-Control")).toContain("no-cache");
    expect(response.headers.get("X-Accel-Buffering")).toBe("no");
    expect(response.body).not.toBeNull();

    const text = await response.text();
    expect(text).toContain("event: step");
    expect(text).toContain("event: done");
  });
});
