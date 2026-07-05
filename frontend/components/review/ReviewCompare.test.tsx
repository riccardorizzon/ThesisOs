import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { ReviewCompare } from "./ReviewCompare";
import { _resetProposalQueueForTests, addProposal } from "@/lib/proposalQueue";
import * as chapterClientModule from "@/lib/chapterClient";

const MOCK_CHAPTER = {
  id: "ch-1",
  parent_id: null,
  order_index: 0,
  title: "Capitolo 1 — Introduzione",
  status: "draft" as const,
  content_md: "Primo paragrafo.\n\nSecondo paragrafo originale.",
  summary: null,
  word_count: 10,
  version: 1,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

afterEach(() => {
  cleanup();
  _resetProposalQueueForTests();
  vi.restoreAllMocks();
});

beforeEach(() => {
  _resetProposalQueueForTests();
});

describe("ReviewCompare", () => {
  it("shows loading skeleton while chapter loads", () => {
    vi.spyOn(chapterClientModule.chapterClient, "get").mockReturnValue(
      new Promise(() => {})
    );

    const proposal = addProposal({
      actionId: "rewrite",
      actionLabel: "Riscrivi",
      chapterId: "ch-1",
      selectionText: "Secondo paragrafo originale.",
      selectionAnchor: null,
      preview: "Secondo paragrafo rivisto.",
    });

    render(<ReviewCompare chapterId="ch-1" proposal={proposal} />);
    expect(screen.getByTestId("review-compare-skeleton")).toBeTruthy();
  });

  it("renders side-by-side columns after load", async () => {
    vi.spyOn(chapterClientModule.chapterClient, "get").mockResolvedValue(MOCK_CHAPTER);

    const proposal = addProposal({
      actionId: "rewrite",
      actionLabel: "Riscrivi",
      chapterId: "ch-1",
      selectionText: "Secondo paragrafo originale.",
      selectionAnchor: null,
      preview: "Secondo paragrafo rivisto.",
    });

    render(<ReviewCompare chapterId="ch-1" proposal={proposal} />);

    await waitFor(() => {
      expect(screen.getByText("Originale")).toBeTruthy();
      expect(screen.getByText("Proposta")).toBeTruthy();
    });
    expect(screen.getByText(/Secondo paragrafo originale/)).toBeTruthy();
    expect(screen.getByText(/Secondo paragrafo rivisto/)).toBeTruthy();
  });

  it("selects hunks and accepts partial with operator confirm", async () => {
    vi.spyOn(chapterClientModule.chapterClient, "get").mockResolvedValue(MOCK_CHAPTER);
    const updateSpy = vi
      .spyOn(chapterClientModule.chapterClient, "update")
      .mockResolvedValue({ ...MOCK_CHAPTER, version: 2 });

    const proposal = addProposal({
      actionId: "rewrite",
      actionLabel: "Riscrivi",
      chapterId: "ch-1",
      selectionText: "Secondo paragrafo originale.",
      selectionAnchor: null,
      preview: "Secondo paragrafo rivisto.",
    });

    const onResolved = vi.fn();
    render(
      <ReviewCompare chapterId="ch-1" proposal={proposal} onResolved={onResolved} />
    );

    await waitFor(() => {
      expect(screen.getByTestId("review-compare")).toBeTruthy();
    });

    const hunkButton = screen.getByText(/Secondo paragrafo rivisto/);
    fireEvent.click(hunkButton);

    fireEvent.click(screen.getByRole("button", { name: "Accetta parziale" }));
    expect(screen.getByTestId("review-confirm-dialog")).toBeTruthy();

    fireEvent.click(screen.getByTestId("review-confirm-yes"));

    await waitFor(() => {
      expect(updateSpy).toHaveBeenCalled();
      expect(onResolved).toHaveBeenCalledWith("partial");
    });
  });

  it("rejects proposal with operator confirm without chapter update", async () => {
    vi.spyOn(chapterClientModule.chapterClient, "get").mockResolvedValue(MOCK_CHAPTER);
    const updateSpy = vi.spyOn(chapterClientModule.chapterClient, "update");

    const proposal = addProposal({
      actionId: "rewrite",
      actionLabel: "Riscrivi",
      chapterId: "ch-1",
      selectionText: null,
      selectionAnchor: null,
      preview: "Testo completamente nuovo.",
    });

    render(<ReviewCompare chapterId="ch-1" proposal={proposal} />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Rifiuta" })).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "Rifiuta" }));
    fireEvent.click(screen.getByTestId("review-confirm-yes"));

    await waitFor(() => {
      expect(updateSpy).not.toHaveBeenCalled();
      expect(screen.getByRole("status")).toHaveTextContent(/rifiutata/i);
    });
  });
});
