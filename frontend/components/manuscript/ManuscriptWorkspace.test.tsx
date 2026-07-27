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
        id: "c3",
        parent_id: null,
        order_index: 7,
        title: "Cap. 3 — Progettazione metodologica",
        status: "review",
        content_md: "# Capitolo 3\n\nIntro capitolo.",
        summary: null,
        word_count: 100,
        version: 1,
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
      },
      {
        id: "s36",
        parent_id: null,
        order_index: 36,
        title: "[kimi] §3.6 Sintesi: il capo come costruzione di senso",
        status: "draft",
        content_md: "# Sintesi\n\nTesto §3.6.",
        summary: null,
        word_count: 177,
        version: 1,
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
      },
    ]);
    vi.mocked(chapterClient.get).mockImplementation(async (id: string) => {
      const all = await chapterClient.list();
      return all.find((c) => c.id === id)!;
    });
  });

  it("shows §3.6 in the outline and links Modifica to Writing", async () => {
    render(<ManuscriptWorkspace chapterId="s36" />);
    await waitFor(() => {
      expect(screen.getByText("3.6")).toBeTruthy();
    });
    expect(screen.getByText("Sintesi: il capo come costruzione di senso")).toBeTruthy();
    expect(screen.getByTestId("manuscript-edit").getAttribute("href")).toBe("/writing/s36");
  });

  it("Prev/Next walks flattened outline order", async () => {
    render(<ManuscriptWorkspace chapterId="s36" />);
    await waitFor(() => screen.getByTestId("manuscript-reader"));
    fireEvent.click(screen.getByRole("button", { name: "Precedente" }));
    expect(push).toHaveBeenCalledWith("/manuscript/c3");
  });
});
