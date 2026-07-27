import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ManuscriptWorkspace } from "./ManuscriptWorkspace";

const push = vi.fn();
const replace = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push, replace }),
}));

vi.mock("@/lib/chapterClient", () => ({
  chapterClient: {
    list: vi.fn(),
    get: vi.fn(),
  },
  ChapterApiError: class ChapterApiError extends Error {
    status = 404;
    code = "not_found";
  },
}));

import { chapterClient } from "@/lib/chapterClient";

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("ManuscriptWorkspace", () => {
  beforeEach(() => {
    vi.mocked(chapterClient.list).mockResolvedValue([
      {
        id: "c1",
        parent_id: null,
        order_index: 0,
        title: "Uno",
        status: "draft",
        content_md: null,
        summary: null,
        word_count: 3,
        version: 1,
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
      },
      {
        id: "c2",
        parent_id: null,
        order_index: 1,
        title: "Due",
        status: "review",
        content_md: null,
        summary: null,
        word_count: 4,
        version: 1,
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
      },
    ]);
    vi.mocked(chapterClient.get).mockImplementation(async (id: string) => ({
      id,
      parent_id: null,
      order_index: id === "c1" ? 0 : 1,
      title: id === "c1" ? "Uno" : "Due",
      status: id === "c1" ? "draft" : "review",
      content_md: id === "c1" ? "# Alpha\n\ntext" : "# Beta\n\nmore words here",
      summary: null,
      word_count: id === "c1" ? 3 : 4,
      version: 1,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    }));
  });

  it("loads TOC sections from fetched content and links Modifica to Writing", async () => {
    render(<ManuscriptWorkspace chapterId="c1" />);
    await waitFor(() => {
      expect(screen.getByTestId("manuscript-workspace")).toBeTruthy();
    });
    expect(screen.getByRole("heading", { level: 1, name: "Alpha" })).toBeTruthy();
    expect(screen.getByTestId("manuscript-edit").getAttribute("href")).toBe("/writing/c1");
  });

  it("Prev/Next push manuscript routes in order", async () => {
    render(<ManuscriptWorkspace chapterId="c1" />);
    await waitFor(() => screen.getByTestId("manuscript-reader"));
    fireEvent.click(screen.getByRole("button", { name: "Successivo" }));
    expect(push).toHaveBeenCalledWith("/manuscript/c2");
  });
});
