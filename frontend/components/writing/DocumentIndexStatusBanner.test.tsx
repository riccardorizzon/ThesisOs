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

  it("treats indexed as a successful terminal status", async () => {
    vi.spyOn(documentClient, "get").mockResolvedValue({
      id: "doc-42",
      title: "Benjamin",
      author: null,
      source_type: "pdf",
      original_filename: "benjamin.pdf",
      gcs_uri: null,
      status: "indexed",
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
      expect(screen.getByTestId("writing-index-parsed-doc-42")).toHaveTextContent(
        /Indicizzato/
      );
    });
    expect(screen.getByTestId("writing-index-status-dismiss")).toBeTruthy();
  });

  it("does not render raw JSON parsing errors", async () => {
    vi.spyOn(documentClient, "get").mockRejectedValue(
      new Error(`Unexpected token '<', "<!DOCTYPE "... is not valid JSON`)
    );

    render(<DocumentIndexStatusBanner />);

    const banner = await screen.findByTestId("writing-index-status-error");
    expect(banner).toHaveTextContent(
      "Impossibile verificare lo stato di indicizzazione. Riprova."
    );
    expect(banner).not.toHaveTextContent(/Unexpected token|DOCTYPE/i);
  });

  it("does not render raw parser failures for failed documents", async () => {
    vi.spyOn(documentClient, "get").mockResolvedValue({
      id: "doc-42",
      title: "Documento non valido",
      author: null,
      source_type: "pdf",
      original_filename: "fake.pdf",
      gcs_uri: null,
      status: "failed",
      page_count: null,
      language: "it",
      version: 1,
      parser: "pdf",
      parsed_at: null,
      chunk_count: null,
      error_message: "pymupdf could not open PDF: Failed to open stream",
      metadata: {},
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-02T00:00:00Z",
    });

    render(<DocumentIndexStatusBanner />);

    const banner = await screen.findByTestId("writing-index-status-banner");
    expect(banner).toHaveTextContent(
      "Indicizzazione fallita. Controlla il file e caricalo di nuovo."
    );
    expect(banner).not.toHaveTextContent(/pymupdf|Failed to open/i);
  });
});
