import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AddToBibliographyButton } from "@/components/sources/AddToBibliographyButton";
import { addSourceToBibliography } from "@/lib/sourcesClient";

vi.mock("@/lib/sourcesClient", () => ({
  addSourceToBibliography: vi.fn(),
}));

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("AddToBibliographyButton", () => {
  it("promotes a candidate source and reports success", async () => {
    vi.mocked(addSourceToBibliography).mockResolvedValue({
      id: "source-1",
      slug: "source-1",
      type: "source",
      title: "Fonte candidata",
      confidence: "non_valutata",
      knowledge_state: "validated",
      linked_counts: {
        sources: 0,
        chapters: 0,
        concepts: 0,
        decisions: 0,
        authors: 0,
        citations: 0,
      },
      created_by: "importazione",
      proposal_state: "nessuna",
      is_core: false,
      related_concepts: [],
      corpus_status: "approvata",
    });
    const onPromoted = vi.fn();
    render(
      <AddToBibliographyButton
        slug="source-1"
        corpusStatus="candidata"
        onPromoted={onPromoted}
      />
    );

    fireEvent.click(
      screen.getByRole("button", { name: "Aggiungi alla bibliografia" })
    );

    await waitFor(() => {
      expect(addSourceToBibliography).toHaveBeenCalledWith("source-1");
    });
    expect(onPromoted).toHaveBeenCalled();
    expect(screen.getByText("Aggiunta alla bibliografia")).toBeInTheDocument();
  });

  it("does not render for an approved source", () => {
    render(
      <AddToBibliographyButton
        slug="source-1"
        corpusStatus="approvata"
      />
    );
    expect(
      screen.queryByRole("button", { name: "Aggiungi alla bibliografia" })
    ).not.toBeInTheDocument();
  });
});
