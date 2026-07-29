import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { ChapterVersionsPanel } from "./ChapterVersionsPanel";
import { chapterClient, ChapterApiError } from "@/lib/chapterClient";

vi.mock("@/lib/chapterClient", () => {
  class ChapterApiError extends Error {
    status: number;
    code: string;
    constructor(status: number, code: string, message: string) {
      super(message);
      this.status = status;
      this.code = code;
    }
  }
  return {
    chapterClient: {
      listVersions: vi.fn(),
      update: vi.fn(),
    },
    ChapterApiError,
  };
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("ChapterVersionsPanel", () => {
  it("loads and lists versions", async () => {
    vi.mocked(chapterClient.listVersions).mockResolvedValue([
      {
        chapter_id: "ch-1",
        version: 2,
        change_kind: "EDIT",
        title: "Cap. 1",
        status: "draft",
        content_md: "v2",
        summary: null,
        word_count: 1,
        metadata: {},
        changed_at: "2026-01-02T00:00:00Z",
      },
      {
        chapter_id: "ch-1",
        version: 1,
        change_kind: "WRITE",
        title: "Cap. 1",
        status: "draft",
        content_md: "v1",
        summary: null,
        word_count: 1,
        metadata: {},
        changed_at: "2026-01-01T00:00:00Z",
      },
    ]);

    render(
      <ChapterVersionsPanel
        open
        chapterId="ch-1"
        expectedVersion={2}
        onClose={vi.fn()}
        onRestored={vi.fn()}
      />
    );

    expect(await screen.findByText(/Versione 2/i)).toBeTruthy();
    expect(screen.getByText(/Versione 1/i)).toBeTruthy();
    expect(chapterClient.listVersions).toHaveBeenCalledWith("ch-1");
  });

  it("restores a version via content PATCH", async () => {
    const onRestored = vi.fn();
    vi.mocked(chapterClient.listVersions).mockResolvedValue([
      {
        chapter_id: "ch-1",
        version: 1,
        change_kind: "WRITE",
        title: "Cap. 1",
        status: "draft",
        content_md: "old content",
        summary: null,
        word_count: 2,
        metadata: {},
        changed_at: "2026-01-01T00:00:00Z",
      },
    ]);
    vi.mocked(chapterClient.update).mockResolvedValue({
      id: "ch-1",
      parent_id: null,
      order_index: 0,
      title: "Cap. 1",
      status: "draft",
      content_md: "old content",
      summary: null,
      word_count: 2,
      version: 3,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-03T00:00:00Z",
    });

    render(
      <ChapterVersionsPanel
        open
        chapterId="ch-1"
        expectedVersion={2}
        onClose={vi.fn()}
        onRestored={onRestored}
      />
    );

    await screen.findByText(/Versione 1/i);
    fireEvent.click(screen.getByTestId("chapter-version-restore-1"));
    fireEvent.click(screen.getByTestId("chapter-version-restore-confirm"));

    await waitFor(() =>
      expect(chapterClient.update).toHaveBeenCalledWith("ch-1", {
        content_md: "old content",
        expected_version: 2,
      })
    );
    expect(onRestored).toHaveBeenCalledWith(
      expect.objectContaining({ content_md: "old content", version: 3 })
    );
  });

  it("clears confirm UI and notifies conflict on 409", async () => {
    const onConflict = vi.fn();
    vi.mocked(chapterClient.listVersions).mockResolvedValue([
      {
        chapter_id: "ch-1",
        version: 1,
        change_kind: "WRITE",
        title: "Cap. 1",
        status: "draft",
        content_md: "old",
        summary: null,
        word_count: 1,
        metadata: {},
        changed_at: "2026-01-01T00:00:00Z",
      },
    ]);
    vi.mocked(chapterClient.update).mockRejectedValue(
      new ChapterApiError(409, "conflict", "Version conflict")
    );

    render(
      <ChapterVersionsPanel
        open
        chapterId="ch-1"
        expectedVersion={2}
        onClose={vi.fn()}
        onRestored={vi.fn()}
        onConflict={onConflict}
      />
    );

    await screen.findByText(/Versione 1/i);
    fireEvent.click(screen.getByTestId("chapter-version-restore-1"));
    expect(screen.getByTestId("chapter-version-restore-dialog")).toBeTruthy();
    fireEvent.click(screen.getByTestId("chapter-version-restore-confirm"));

    await waitFor(() => expect(onConflict).toHaveBeenCalled());
    expect(screen.queryByTestId("chapter-version-restore-dialog")).toBeNull();
  });
});
