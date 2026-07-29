import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";

import { ExportMenu } from "./ExportMenu";
import { chapterClient } from "@/lib/chapterClient";

vi.mock("@/lib/chapterClient", () => ({
  chapterClient: {
    exportMarkdown: vi.fn(),
    exportManuscriptMarkdown: vi.fn(),
  },
}));

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("ExportMenu", () => {
  it("keeps trigger enabled without chapter so manuscript export stays available", () => {
    render(<ExportMenu chapterId={null} />);
    expect(screen.getByTestId("export-menu-trigger")).not.toBeDisabled();
    fireEvent.click(screen.getByTestId("export-menu-trigger"));
    expect(screen.getByTestId("chapter-export-md")).toBeDisabled();
    expect(screen.getByTestId("manuscript-export-md")).not.toBeDisabled();
  });

  it("allows manuscript export when chapter export is disabled (read-only)", () => {
    render(<ExportMenu chapterId="ch-1" chapterExportDisabled />);
    fireEvent.click(screen.getByTestId("export-menu-trigger"));
    expect(screen.getByTestId("chapter-export-md")).toBeDisabled();
    expect(screen.getByTestId("manuscript-export-md")).not.toBeDisabled();
  });

  it("exports markdown when menu item clicked", async () => {
    const blob = new Blob(["# Hello"], { type: "text/markdown" });
    vi.mocked(chapterClient.exportMarkdown).mockResolvedValue(blob);
    const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});

    render(<ExportMenu chapterId="ch-1" />);
    fireEvent.click(screen.getByTestId("export-menu-trigger"));
    fireEvent.click(screen.getByTestId("chapter-export-md"));

    await waitFor(() =>
      expect(chapterClient.exportMarkdown).toHaveBeenCalledWith("ch-1")
    );
    clickSpy.mockRestore();
  });

  it("exports full manuscript markdown", async () => {
    const blob = new Blob(["# Manoscritto"], { type: "text/markdown" });
    vi.mocked(chapterClient.exportManuscriptMarkdown).mockResolvedValue(blob);
    const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});

    render(<ExportMenu chapterId="ch-1" />);
    fireEvent.click(screen.getByTestId("export-menu-trigger"));
    fireEvent.click(screen.getByTestId("manuscript-export-md"));

    await waitFor(() =>
      expect(chapterClient.exportManuscriptMarkdown).toHaveBeenCalled()
    );
    clickSpy.mockRestore();
  });

  it("calls onError when export fails", async () => {
    vi.mocked(chapterClient.exportMarkdown).mockRejectedValue(new Error("fail"));
    const onError = vi.fn();

    render(<ExportMenu chapterId="ch-1" onError={onError} />);
    fireEvent.click(screen.getByTestId("export-menu-trigger"));
    fireEvent.click(screen.getByTestId("chapter-export-md"));

    await waitFor(() => expect(onError).toHaveBeenCalled());
  });
});
