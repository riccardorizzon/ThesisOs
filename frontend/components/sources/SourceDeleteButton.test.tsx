import { describe, expect, it, vi, afterEach } from "vitest";
import { render, screen, cleanup, fireEvent, waitFor } from "@testing-library/react";

import { SourceDeleteButton } from "./SourceDeleteButton";

const push = vi.fn();
const refresh = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push, refresh }),
}));

vi.mock("@/lib/sourcesClient", () => ({
  deleteSource: vi.fn().mockResolvedValue(undefined),
}));

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("SourceDeleteButton", () => {
  it("shows confirm dialog then deletes", async () => {
    const { deleteSource } = await import("@/lib/sourcesClient");
    render(<SourceDeleteButton slug="doc-1" title="Mia fonte" />);

    fireEvent.click(screen.getByTestId("source-delete-trigger"));
    expect(screen.getByTestId("source-delete-confirm")).toBeTruthy();

    fireEvent.click(screen.getByTestId("source-delete-confirm-yes"));

    await waitFor(() => {
      expect(deleteSource).toHaveBeenCalledWith("doc-1");
    });
    expect(push).toHaveBeenCalledWith("/sources");
    expect(refresh).toHaveBeenCalled();
  });

  it("cancels without deleting", () => {
    render(<SourceDeleteButton slug="doc-1" title="Mia fonte" />);

    fireEvent.click(screen.getByTestId("source-delete-trigger"));
    fireEvent.click(screen.getByTestId("source-delete-confirm-no"));

    expect(screen.queryByTestId("source-delete-confirm")).toBeNull();
    expect(screen.getByTestId("source-delete-trigger")).toBeTruthy();
  });
});
