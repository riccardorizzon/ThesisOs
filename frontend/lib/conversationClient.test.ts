import { afterEach, describe, expect, it, vi } from "vitest";

import {
  deleteConversation,
  renameConversation,
} from "@/lib/conversationClient";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("conversation lifecycle client", () => {
  it("renames a conversation within the active project", async () => {
    const fetchMock = vi.spyOn(global, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          id: "conv-1",
          project_id: "thesis-agent",
          title: "Nuovo titolo",
          created_at: "2026-01-01T00:00:00Z",
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }
      )
    );

    await renameConversation("conv-1", "Nuovo titolo", "thesis-agent");

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining(
        "/conversations/conv-1?project_id=thesis-agent"
      ),
      expect.objectContaining({
        method: "PATCH",
        body: JSON.stringify({ title: "Nuovo titolo" }),
      })
    );
  });

  it("deletes a conversation within the active project", async () => {
    const fetchMock = vi.spyOn(global, "fetch").mockResolvedValue(
      new Response(null, { status: 204 })
    );

    await deleteConversation("conv-1", "thesis-agent");

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining(
        "/conversations/conv-1?project_id=thesis-agent"
      ),
      expect.objectContaining({ method: "DELETE" })
    );
  });
});
