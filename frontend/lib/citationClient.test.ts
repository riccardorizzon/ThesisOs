import { afterEach, describe, expect, it, vi } from "vitest";

import { validateProjectCitations } from "@/lib/citationClient";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("validateProjectCitations", () => {
  it("posts text and project scope to the citation validator", async () => {
    const fetchMock = vi.spyOn(global, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ issues: [], blocking: false }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      })
    );

    await validateProjectCitations("thesis-002", "(Benjamin, 1936)");

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/citations/validate"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          project_id: "thesis-002",
          text: "(Benjamin, 1936)",
        }),
      })
    );
  });

  it("maps transport failures to product copy", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(
      new Response("<!DOCTYPE html>", {
        status: 500,
        headers: { "Content-Type": "text/html" },
      })
    );

    await expect(
      validateProjectCitations("thesis-002", "(Benjamin, 1936)")
    ).rejects.toThrow("Verifica citazioni non disponibile. Riprova.");
  });
});
