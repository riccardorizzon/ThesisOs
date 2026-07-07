import { describe, expect, it, vi, afterEach } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { DocumentIndexStatusBanner } from "./DocumentIndexStatusBanner";
import { documentClient } from "@/lib/documentClient";

vi.mock("next/navigation", () => ({
  useSearchParams: () => new URLSearchParams("document=doc-42"),
}));

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("Writing DocumentIndexStatus", () => {
  it("shows pending indexing status for tracked document", async () => {
    vi.spyOn(documentClient, "get").mockResolvedValue({
      id: "doc-42",
      title: "Benjamin",
      author: null,
      source_type: "pdf",
      original_filename: "benjamin.pdf",
      gcs_uri: null,
      status: "processing",
      page_count: 120,
      language: "it",
      version: 1,
      parser: "pdf",
      parsed_at: null,
      chunk_count: 12,
      error_message: null,
      metadata: {},
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    });

    render(<DocumentIndexStatusBanner />);

    await waitFor(() => {
      expect(screen.getByTestId("writing-index-status-banner")).toBeTruthy();
    });
    expect(screen.getByTestId("writing-index-pending-doc-42")).toHaveTextContent(
      /Indicizzazione in corso/
    );
  });

  it("shows parsed status with dismiss control", async () => {
    vi.spyOn(documentClient, "get").mockResolvedValue({
      id: "doc-42",
      title: "Benjamin",
      author: null,
      source_type: "pdf",
      original_filename: "benjamin.pdf",
      gcs_uri: null,
      status: "parsed",
      page_count: 120,
      language: "it",
      version: 1,
      parser: "pdf",
      parsed_at: "2026-01-02T00:00:00Z",
      chunk_count: 48,
      error_message: null,
      metadata: {},
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-02T00:00:00Z",
    });

    render(<DocumentIndexStatusBanner />);

    await waitFor(() => {
      expect(screen.getByTestId("writing-index-parsed-doc-42")).toHaveTextContent(/Indicizzato/);
    });
    expect(screen.getByTestId("writing-index-status-dismiss")).toBeTruthy();
  });
});
