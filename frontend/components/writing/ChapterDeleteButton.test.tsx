import { describe, expect, it, vi, afterEach } from "vitest";
import { render, screen, cleanup, fireEvent, waitFor } from "@testing-library/react";

import { ChapterDeleteButton } from "./ChapterDeleteButton";
import { chapterClient } from "@/lib/chapterClient";

const push = vi.fn();
const refresh = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push, replace: vi.fn(), refresh }),
}));

vi.mock("@/lib/chapterClient", () => ({
  chapterClient: {
    delete: vi.fn(),
  },
}));

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("ChapterDeleteButton", () => {
  it("shows confirm dialog then deletes", async () => {
    vi.mocked(chapterClient.delete).mockResolvedValue(undefined);
    const onDeleted = vi.fn();

    render(
      <ChapterDeleteButton
        chapterId="ch-1"
        title="Introduzione"
        onDeleted={onDeleted}
      />
    );

    fireEvent.click(screen.getByTestId("chapter-delete-trigger"));
    fireEvent.click(screen.getByTestId("chapter-delete-confirm-yes"));

    await waitFor(() => {
      expect(chapterClient.delete).toHaveBeenCalledWith("ch-1");
    });
    expect(onDeleted).toHaveBeenCalled();
    expect(push).toHaveBeenCalledWith("/writing");
    expect(refresh).toHaveBeenCalled();
  });
});
