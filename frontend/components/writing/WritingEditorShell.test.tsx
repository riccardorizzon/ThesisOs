import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { WritingEditorShell } from "./WritingEditorShell";
import { chapterClient } from "@/lib/chapterClient";

vi.mock("@/lib/chapterClient", () => ({
  chapterClient: {
    get: vi.fn(),
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

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("WritingEditorShell", () => {
  it("prompts to select a chapter when no chapterId", () => {
    render(<WritingEditorShell />);

    expect(screen.getByRole("region", { name: "Editor Markdown" })).toBeTruthy();
    expect(
      screen.getByText(/Scegli un capitolo dall'outline/i)
    ).toBeTruthy();
  });

  it("loads chapter content from API", async () => {
    vi.mocked(chapterClient.get).mockResolvedValue({
      id: "2",
      parent_id: null,
      order_index: 1,
      title: "Cap. 2 — Quadro teorico",
      status: "review",
      content_md: "# Capitolo 2\n\nContenuto.",
      summary: null,
      word_count: 3,
      version: 1,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    });

    render(<WritingEditorShell chapterId="2" />);

    await waitFor(() =>
      expect(screen.getByRole("textbox", { name: "Contenuto capitolo" })).toHaveValue(
        "# Capitolo 2\n\nContenuto."
      )
    );
  });
});
