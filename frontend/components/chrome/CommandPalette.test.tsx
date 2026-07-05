import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { CommandPalette } from "./CommandPalette";

const push = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

vi.mock("@/lib/chapterClient", () => ({
  chapterClient: {
    list: vi.fn().mockResolvedValue([
      {
        id: "3",
        parent_id: null,
        order_index: 2,
        title: "Cap. 3 — Analisi",
        status: "draft",
        content_md: null,
        summary: null,
        word_count: 0,
        version: 1,
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
      },
    ]),
  },
}));

beforeEach(() => {
  push.mockReset();
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: false,
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    })),
  });
});

afterEach(() => {
  cleanup();
});

describe("CommandPalette", () => {
  it("opens and focuses search input", async () => {
    const onClose = vi.fn();
    render(<CommandPalette open onClose={onClose} />);

    expect(screen.getByRole("dialog", { name: "Palette comandi" })).toBeTruthy();
    await waitFor(() =>
      expect(screen.getByTestId("command-palette-input")).toHaveFocus()
    );
  });

  it("filters actions by search query", async () => {
    render(<CommandPalette open onClose={vi.fn()} />);

    fireEvent.change(screen.getByTestId("command-palette-input"), {
      target: { value: "fonti" },
    });

    await waitFor(() => {
      expect(screen.getByTestId("command-action-goto-sources")).toBeTruthy();
      expect(screen.queryByTestId("command-action-goto-home")).toBeNull();
    });
  });

  it("executes navigation action and closes", async () => {
    const onClose = vi.fn();
    render(<CommandPalette open onClose={onClose} />);

    fireEvent.click(screen.getByTestId("command-action-nav-/writing"));

    expect(push).toHaveBeenCalledWith("/writing");
    expect(onClose).toHaveBeenCalled();
  });
});
