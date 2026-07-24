import { afterEach, describe, expect, it, vi } from "vitest";

import { deleteProject } from "@/lib/projectsClient";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("deleteProject", () => {
  it("sends the exact project confirmation in a DELETE body", async () => {
    const fetchMock = vi.spyOn(global, "fetch").mockResolvedValue(
      new Response(null, { status: 204 })
    );

    await deleteProject("thesis-002", "thesis-002");

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/projects/thesis-002"),
      expect.objectContaining({
        method: "DELETE",
        body: JSON.stringify({ confirmation_project_id: "thesis-002" }),
      })
    );
  });

  it("maps protected project errors to product copy", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          code: "protected_project",
          message: "backend detail",
        }),
        {
          status: 403,
          headers: { "Content-Type": "application/json" },
        }
      )
    );

    await expect(
      deleteProject("thesis-agent", "thesis-agent")
    ).rejects.toThrow("Questa tesi è protetta e non può essere eliminata.");
  });
});
