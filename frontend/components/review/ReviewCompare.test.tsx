import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { ReviewCompare } from "./ReviewCompare";
import { _resetProposalQueueForTests, _seedProposalQueueForTests } from "@/lib/proposalQueue";
import * as chapterClientModule from "@/lib/chapterClient";
import * as proposalClientModule from "@/lib/proposalClient";

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

const SAMPLE_PROPOSAL = {
  id: "prop-test-1",
  actionId: "rewrite",
  actionLabel: "Riscrivi",
  chapterId: "ch-1",
  selectionText: "Secondo paragrafo originale.",
  selectionAnchor: null,
  preview: "Primo paragrafo.\n\nSecondo paragrafo rivisto.",
  status: "pending" as const,
  createdAt: "2026-01-01T00:00:00Z",
};

afterEach(() => {
  cleanup();
  _resetProposalQueueForTests();
  vi.restoreAllMocks();
});

beforeEach(() => {
  _resetProposalQueueForTests();
  vi.spyOn(proposalClientModule.proposalClient, "accept").mockResolvedValue({
    chapter: { ...MOCK_CHAPTER, version: 2, content_md: SAMPLE_PROPOSAL.preview },
  });
  vi.spyOn(proposalClientModule.proposalClient, "reject").mockResolvedValue({
    proposal: {
      id: SAMPLE_PROPOSAL.id,
      project_id: "thesis-agent",
      chapter_id: "ch-1",
      status: "rejected",
      original: SAMPLE_PROPOSAL.selectionText ?? "",
      proposed: SAMPLE_PROPOSAL.preview,
      action: "rewrite",
      created_at: SAMPLE_PROPOSAL.createdAt,
    },
  });
});

describe("ReviewCompare", () => {
  it("shows loading skeleton while chapter loads", () => {
    vi.spyOn(chapterClientModule.chapterClient, "get").mockReturnValue(
      new Promise(() => {})
    );

    _seedProposalQueueForTests([SAMPLE_PROPOSAL]);

    render(<ReviewCompare chapterId="ch-1" proposal={SAMPLE_PROPOSAL} />);
    expect(screen.getByTestId("review-compare-skeleton")).toBeTruthy();
  });

  it("renders side-by-side columns after load", async () => {
    vi.spyOn(chapterClientModule.chapterClient, "get").mockResolvedValue(MOCK_CHAPTER);

    render(<ReviewCompare chapterId="ch-1" proposal={SAMPLE_PROPOSAL} />);

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
    const rejectSpy = vi.spyOn(proposalClientModule.proposalClient, "reject");
    _seedProposalQueueForTests([SAMPLE_PROPOSAL]);

    const onResolved = vi.fn();
    render(
      <ReviewCompare chapterId="ch-1" proposal={SAMPLE_PROPOSAL} onResolved={onResolved} />
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
      expect(rejectSpy).toHaveBeenCalledWith(SAMPLE_PROPOSAL.id, { reason: "partial_accept" });
      expect(onResolved).toHaveBeenCalledWith("partial");
    });
  });

  it("accepts all via proposals API", async () => {
    vi.spyOn(chapterClientModule.chapterClient, "get").mockResolvedValue(MOCK_CHAPTER);
    const acceptSpy = vi.spyOn(proposalClientModule.proposalClient, "accept");
    const updateSpy = vi.spyOn(chapterClientModule.chapterClient, "update");

    render(<ReviewCompare chapterId="ch-1" proposal={SAMPLE_PROPOSAL} />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Accetta tutto" })).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "Accetta tutto" }));
    fireEvent.click(screen.getByTestId("review-confirm-yes"));

    await waitFor(() => {
      expect(acceptSpy).toHaveBeenCalledWith(SAMPLE_PROPOSAL.id, {
        expected_chapter_version: 1,
      });
      expect(updateSpy).not.toHaveBeenCalled();
    });
  });

  it("rejects proposal with operator confirm without chapter update", async () => {
    vi.spyOn(chapterClientModule.chapterClient, "get").mockResolvedValue(MOCK_CHAPTER);
    const updateSpy = vi.spyOn(chapterClientModule.chapterClient, "update");
    const rejectSpy = vi.spyOn(proposalClientModule.proposalClient, "reject");
    _seedProposalQueueForTests([SAMPLE_PROPOSAL]);

    render(<ReviewCompare chapterId="ch-1" proposal={SAMPLE_PROPOSAL} />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Rifiuta" })).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "Rifiuta" }));
    fireEvent.click(screen.getByTestId("review-confirm-yes"));

    await waitFor(() => {
      expect(rejectSpy).toHaveBeenCalledWith(SAMPLE_PROPOSAL.id);
      expect(updateSpy).not.toHaveBeenCalled();
      expect(screen.getByRole("status")).toHaveTextContent(/rifiutata/i);
    });
  });
});
