import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";

import { ExportMenu } from "./ExportMenu";
import { chapterClient } from "@/lib/chapterClient";

vi.mock("@/lib/chapterClient", () => ({
  chapterClient: {
    exportMarkdown: vi.fn(),
  },
}));

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("ExportMenu", () => {
  it("disables trigger when no chapter", () => {
    render(<ExportMenu chapterId={null} />);
    expect(screen.getByTestId("export-menu-trigger")).toBeDisabled();
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

  it("calls onError when export fails", async () => {
    vi.mocked(chapterClient.exportMarkdown).mockRejectedValue(new Error("fail"));
    const onError = vi.fn();

    render(<ExportMenu chapterId="ch-1" onError={onError} />);
    fireEvent.click(screen.getByTestId("export-menu-trigger"));
    fireEvent.click(screen.getByTestId("chapter-export-md"));

    await waitFor(() => expect(onError).toHaveBeenCalled());
  });
});
