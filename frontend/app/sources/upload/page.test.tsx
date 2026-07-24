import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import SourceUploadPage from "@/app/sources/upload/page";

const push = vi.fn();
const refresh = vi.fn();
const upload = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push, refresh }),
}));

vi.mock("@/lib/documentStore", () => ({
  useDocumentStore: () => ({
    upload,
    loading: false,
    error: null,
    errorCode: null,
    errorStatus: null,
    clearError: vi.fn(),
  }),
}));

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("SourceUploadPage", () => {
  it("declares every format accepted by the backend", () => {
    render(<SourceUploadPage />);

    expect(
      screen.getByText(/PDF, EPUB, DOCX, Markdown o testo/)
    ).toBeInTheDocument();
    expect(screen.getByTestId("source-file-input")).toHaveAttribute(
      "accept",
      ".pdf,.epub,.docx,.md,.markdown,.txt"
    );
  });

  it("refreshes Sources after a successful upload to avoid stale prefetched data", async () => {
    upload.mockResolvedValue({ id: "document-1" });
    render(<SourceUploadPage />);
    const file = new File(["# Metodo"], "metodo.md", {
      type: "text/markdown",
    });
    fireEvent.change(screen.getByTestId("source-file-input"), {
      target: { files: [file] },
    });

    fireEvent.click(screen.getByRole("button", { name: "Aggiungi fonte" }));

    await waitFor(() => expect(upload).toHaveBeenCalled());
    expect(push).toHaveBeenCalledWith("/sources?document=document-1");
    expect(refresh).toHaveBeenCalled();
  });
});
