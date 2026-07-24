import { afterEach, describe, expect, it, vi } from "vitest";

import { addSourceToBibliography } from "@/lib/sourcesClient";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("addSourceToBibliography", () => {
  it("posts to the project-scoped source action", async () => {
    const fetchMock = vi.spyOn(global, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          id: "source-1",
          slug: "source-1",
          type: "source",
          title: "Fonte",
          confidence: "non_valutata",
          knowledge_state: "validated",
          linked_counts: {},
          created_by: "importazione",
          proposal_state: "nessuna",
          is_core: false,
          related_concepts: [],
          corpus_status: "approvata",
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }
      )
    );

    await addSourceToBibliography("source-1", "thesis-002");

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining(
        "/projects/thesis-002/sources/source-1/bibliography"
      ),
      expect.objectContaining({ method: "POST" })
    );
  });
});
