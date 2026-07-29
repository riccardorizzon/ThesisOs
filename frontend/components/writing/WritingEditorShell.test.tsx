import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { WritingEditorShell } from "./WritingEditorShell";
import { chapterClient, type Chapter } from "@/lib/chapterClient";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), refresh: vi.fn() }),
}));

vi.mock("@/lib/chapterClient", () => ({
  chapterClient: {
    get: vi.fn(),
    update: vi.fn(),
    listVersions: vi.fn(),
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

const baseChapter: Chapter = {
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
};

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

  it("shows delete button for deletable chapters", async () => {
    vi.mocked(chapterClient.get).mockResolvedValue({
      id: "user-ch",
      parent_id: null,
      order_index: 0,
      title: "Introduzione",
      status: "draft",
      content_md: "",
      summary: null,
      word_count: 0,
      version: 1,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
      deletable: true,
    });

    render(<WritingEditorShell chapterId="user-ch" />);

    expect(await screen.findByTestId("chapter-delete-trigger")).toBeTruthy();
  });

  it("renames chapter via inline title edit", async () => {
    const onChapterUpdated = vi.fn();
    vi.mocked(chapterClient.get).mockResolvedValue(baseChapter);
    vi.mocked(chapterClient.update).mockResolvedValue({
      ...baseChapter,
      title: "Cap. 2 — Nuovo titolo",
      version: 2,
    });

    render(<WritingEditorShell chapterId="2" onChapterUpdated={onChapterUpdated} />);

    await screen.findByTestId("chapter-title-display");
    fireEvent.click(screen.getByTestId("chapter-title-display"));
    const input = screen.getByTestId("chapter-title-input");
    fireEvent.change(input, { target: { value: "Cap. 2 — Nuovo titolo" } });
    fireEvent.keyDown(input, { key: "Enter" });

    await waitFor(() =>
      expect(chapterClient.update).toHaveBeenCalledWith("2", {
        title: "Cap. 2 — Nuovo titolo",
        expected_version: 1,
      })
    );
    await waitFor(() =>
      expect(onChapterUpdated).toHaveBeenCalledWith(
        expect.objectContaining({ title: "Cap. 2 — Nuovo titolo", version: 2 })
      )
    );
  });

  it("updates chapter status from select", async () => {
    const onChapterUpdated = vi.fn();
    vi.mocked(chapterClient.get).mockResolvedValue(baseChapter);
    vi.mocked(chapterClient.update).mockResolvedValue({
      ...baseChapter,
      status: "approved",
      version: 2,
    });

    render(<WritingEditorShell chapterId="2" onChapterUpdated={onChapterUpdated} />);

    const select = await screen.findByTestId("chapter-status-select");
    fireEvent.change(select, { target: { value: "approved" } });

    await waitFor(() =>
      expect(chapterClient.update).toHaveBeenCalledWith("2", {
        status: "approved",
        expected_version: 1,
      })
    );
    await waitFor(() =>
      expect(onChapterUpdated).toHaveBeenCalledWith(
        expect.objectContaining({ status: "approved", version: 2 })
      )
    );
  });

  it("toggles markdown preview while keeping editor mounted", async () => {
    vi.mocked(chapterClient.get).mockResolvedValue(baseChapter);

    render(<WritingEditorShell chapterId="2" />);

    await screen.findByRole("textbox", { name: "Contenuto capitolo" });
    fireEvent.click(screen.getByTestId("writing-preview-toggle"));

    expect(screen.getByTestId("writing-preview")).toBeTruthy();
    expect(screen.getByTestId("manuscript-markdown")).toBeTruthy();
    // Editor stays mounted (hidden) so pending autosave is not cancelled.
    expect(
      screen.getByRole("textbox", { name: "Contenuto capitolo", hidden: true })
    ).toBeTruthy();

    fireEvent.click(screen.getByTestId("writing-preview-toggle"));
    expect(screen.queryByTestId("writing-preview")).toBeNull();
    expect(screen.getByRole("textbox", { name: "Contenuto capitolo" })).toBeTruthy();
  });

  it("cancels title rename on Escape without saving", async () => {
    vi.mocked(chapterClient.get).mockResolvedValue(baseChapter);

    render(<WritingEditorShell chapterId="2" />);

    await screen.findByTestId("chapter-title-display");
    fireEvent.click(screen.getByTestId("chapter-title-display"));
    const input = screen.getByTestId("chapter-title-input");
    fireEvent.change(input, { target: { value: "Cap. 2 — Annullato" } });
    fireEvent.keyDown(input, { key: "Escape" });

    expect(screen.getByTestId("chapter-title-display")).toBeTruthy();
    expect(chapterClient.update).not.toHaveBeenCalled();
  });

  it("opens cronologia panel", async () => {
    vi.mocked(chapterClient.get).mockResolvedValue(baseChapter);
    vi.mocked(chapterClient.listVersions).mockResolvedValue([]);

    render(<WritingEditorShell chapterId="2" />);

    await screen.findByTestId("writing-versions-toggle");
    fireEvent.click(screen.getByTestId("writing-versions-toggle"));
    expect(await screen.findByTestId("chapter-versions-panel")).toBeTruthy();
  });
});
