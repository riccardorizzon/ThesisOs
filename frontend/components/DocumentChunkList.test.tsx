import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { DocumentChunkList } from "@/components/DocumentChunkList";
import type { DocumentChunk } from "@/lib/documentClient";

const longChunk: DocumentChunk = {
  id: "c1",
  document_id: "d1",
  chunk_index: 0,
  chunk_hash: "h",
  content: "x".repeat(500),
  page_from: 1,
  page_to: 2,
  section_path: "Intro",
  token_count: 100,
  metadata: {},
  created_at: "",
};

describe("DocumentChunkList", () => {
  it("renders a truncated preview and no search box (verification-only)", () => {
    render(<DocumentChunkList chunks={[longChunk]} />);
    expect(screen.getByTestId("document-chunk-list")).toBeInTheDocument();
    // preview is 200 chars + ellipsis, not the full 500-char content
    const cell = screen.getByText((t) => t.startsWith("x".repeat(200)) && t.endsWith("…"));
    expect(cell.textContent?.length).toBe(201);
    // M3 guardrail: chunk list is not a search surface
    expect(screen.queryByRole("textbox")).toBeNull();
  });

  it("shows empty state when not parsed", () => {
    render(<DocumentChunkList chunks={[]} />);
    expect(screen.getByText(/No chunks yet/)).toBeInTheDocument();
  });
});
