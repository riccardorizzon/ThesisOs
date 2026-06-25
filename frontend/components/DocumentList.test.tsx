import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { DocumentList } from "@/components/DocumentList";
import type { Document } from "@/lib/documentClient";

const sample: Document[] = [
  {
    id: "a",
    title: "Thesis source",
    author: null,
    source_type: "pdf",
    original_filename: "a.pdf",
    gcs_uri: null,
    status: "parsed",
    page_count: 10,
    language: "it",
    version: 2,
    parser: "docling",
    parsed_at: null,
    chunk_count: 7,
    error_message: null,
    metadata: {},
    created_at: "2026-06-25T10:00:00Z",
    updated_at: "2026-06-25T11:00:00Z",
  },
];

describe("DocumentList", () => {
  it("renders rows with status badge and chunk count", () => {
    render(<DocumentList items={sample} />);
    expect(screen.getByTestId("document-list")).toBeInTheDocument();
    expect(screen.getByText("Thesis source")).toBeInTheDocument();
    expect(screen.getByTestId("status-badge-parsed")).toBeInTheDocument();
    expect(screen.getByText("7")).toBeInTheDocument();
  });

  it("shows empty state", () => {
    render(<DocumentList items={[]} />);
    expect(screen.getByText("No documents found.")).toBeInTheDocument();
  });
});
