import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { KnowledgeWorkspace } from "@/components/knowledge/KnowledgeWorkspace";

vi.mock("@/components/knowledge/notes/KnowledgeNotesPanel", () => ({
  KnowledgeNotesPanel: () => <div>Notes panel</div>,
}));

afterEach(cleanup);

describe("KnowledgeWorkspace", () => {
  it("uses concepts as the default internal view", () => {
    render(<KnowledgeWorkspace concepts={[]} view="concepts" />);

    expect(screen.getByRole("link", { name: "Concetti" })).toHaveAttribute(
      "aria-current",
      "page"
    );
    expect(screen.getByRole("link", { name: "Note" })).toHaveAttribute(
      "href",
      "/knowledge?view=notes"
    );
    expect(screen.getByRole("heading", { name: "Knowledge" })).toBeInTheDocument();
  });

  it("renders notes without adding a top-level module", () => {
    render(<KnowledgeWorkspace concepts={[]} view="notes" />);
    expect(screen.getByText("Notes panel")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Note" })).toHaveAttribute(
      "aria-current",
      "page"
    );
  });
});
