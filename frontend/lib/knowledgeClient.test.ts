import { beforeEach, describe, expect, it, vi } from "vitest";

import { apiBaseUrl } from "@/lib/apiBase";
import { listKnowledgeObjects } from "@/lib/knowledgeClient";

vi.mock("@/lib/apiBase", () => ({
  apiBaseUrl: vi.fn(() => "http://internal-backend:8000"),
}));

describe("knowledgeClient", () => {
  beforeEach(() => {
    vi.mocked(apiBaseUrl).mockReturnValue("http://internal-backend:8000");
  });

  it("listKnowledgeObjects uses apiBaseUrl for SSR-safe backend host", async () => {
    const fetchMock = vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ objects: [] }),
    } as Response);

    await listKnowledgeObjects({ type: "concept" });

    const url = fetchMock.mock.calls[0][0] as string;
    expect(url).toMatch(
      /^http:\/\/internal-backend:8000\/projects\/thesis-agent\/knowledge\/objects/
    );
    expect(url).toContain("type=concept");
  });
});
