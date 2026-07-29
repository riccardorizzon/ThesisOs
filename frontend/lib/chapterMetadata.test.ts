import { beforeEach, describe, expect, it, vi } from "vitest";
import { chapterClient, ChapterApiError } from "@/lib/chapterClient";
import { persistChapterMetadata } from "@/lib/chapterMetadata";

vi.mock("@/lib/chapterClient", () => ({
  chapterClient: {
    update: vi.fn(),
  },
  ChapterApiError: class ChapterApiError extends Error {
    status: number;
    code: string;
    constructor(status: number, code: string, message: string) {
      super(message);
      this.status = status;
      this.code = code;
    }
  },
}));

describe("persistChapterMetadata", () => {
  beforeEach(() => {
    vi.mocked(chapterClient.update).mockReset();
  });

  it("updates title with trimmed value and expected_version", async () => {
    const updated = {
      id: "ch-1",
      parent_id: null,
      order_index: 0,
      title: "Cap. 1 — Intro",
      status: "draft" as const,
      content_md: "",
      summary: null,
      word_count: 0,
      version: 2,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    };
    vi.mocked(chapterClient.update).mockResolvedValue(updated);

    const result = await persistChapterMetadata(
      { id: "ch-1", version: 1 },
      { title: "  Cap. 1 — Intro  " }
    );

    expect(chapterClient.update).toHaveBeenCalledWith("ch-1", {
      title: "Cap. 1 — Intro",
      expected_version: 1,
    });
    expect(result).toEqual(updated);
  });

  it("rejects empty title", async () => {
    await expect(
      persistChapterMetadata({ id: "ch-1", version: 1 }, { title: "   " })
    ).rejects.toThrow("Titolo obbligatorio");
    expect(chapterClient.update).not.toHaveBeenCalled();
  });

  it("updates status", async () => {
    const updated = {
      id: "ch-1",
      parent_id: null,
      order_index: 0,
      title: "Cap. 1",
      status: "review" as const,
      content_md: "",
      summary: null,
      word_count: 0,
      version: 2,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    };
    vi.mocked(chapterClient.update).mockResolvedValue(updated);

    await persistChapterMetadata({ id: "ch-1", version: 1 }, { status: "review" });

    expect(chapterClient.update).toHaveBeenCalledWith("ch-1", {
      status: "review",
      expected_version: 1,
    });
  });

  it("propagates ChapterApiError from update", async () => {
    vi.mocked(chapterClient.update).mockRejectedValue(
      new ChapterApiError(409, "conflict", "Version conflict")
    );

    await expect(
      persistChapterMetadata({ id: "ch-1", version: 1 }, { title: "Nuovo" })
    ).rejects.toMatchObject({ status: 409, code: "conflict" });
  });
});
