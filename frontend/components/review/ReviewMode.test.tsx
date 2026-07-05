import { describe, expect, it, vi, afterEach, beforeEach } from "vitest";
import { render, screen, cleanup, fireEvent, waitFor } from "@testing-library/react";
import { ReviewMode } from "./ReviewMode";
import {
  _resetProposalQueueForTests,
  addProposal,
} from "@/lib/proposalQueue";
import * as chapterClientModule from "@/lib/chapterClient";
import { dispatchOpenReview } from "./reviewIntegration";

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    className,
  }: {
    children: React.ReactNode;
    href: string;
    className?: string;
  }) => (
    <a href={href} className={className}>
      {children}
    </a>
  ),
}));

const searchParams = new URLSearchParams();
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
  }),
  useSearchParams: () => searchParams,
}));

vi.mock("@/components/context/WritingContextBar", () => ({
  WritingContextBar: () => <div data-testid="writing-context-bar" />,
}));

afterEach(() => {
  cleanup();
  _resetProposalQueueForTests();
  vi.restoreAllMocks();
  searchParams.delete("chapter");
  searchParams.delete("proposal");
});

beforeEach(() => {
  _resetProposalQueueForTests();
  vi.spyOn(chapterClientModule.chapterClient, "list").mockResolvedValue([
    {
      id: "ch-1",
      parent_id: null,
      order_index: 0,
      title: "Capitolo 1 — Introduzione",
      status: "draft",
      content_md: "Contenuto.",
      summary: null,
      word_count: 1,
      version: 1,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    },
  ]);
  vi.spyOn(chapterClientModule.chapterClient, "get").mockResolvedValue({
    id: "ch-1",
    parent_id: null,
    order_index: 0,
    title: "Capitolo 1 — Introduzione",
    status: "draft",
    content_md: "Primo.\n\nSecondo originale.",
    summary: null,
    word_count: 2,
    version: 1,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  });
});

describe("ReviewMode", () => {
  it("renders review shell with workflow steps and ContextBar", async () => {
    addProposal({
      actionId: "rewrite",
      actionLabel: "Riscrivi",
      chapterId: "ch-1",
      selectionText: "Secondo originale.",
      selectionAnchor: null,
      preview: "Secondo rivisto.",
    });

    render(<ReviewMode />);

    expect(screen.getByRole("heading", { name: "Revisione" })).toBeTruthy();
    expect(screen.getByRole("navigation", { name: "Passi revisione" })).toBeTruthy();
    expect(screen.getByTestId("writing-context-bar")).toBeTruthy();
    await waitFor(() => {
      expect(screen.getByText("Capitolo 1 — Introduzione")).toBeTruthy();
    });
  });

  it("links to /ai as distinct power mode", () => {
    render(<ReviewMode />);
    expect(screen.getByRole("link", { name: "/ai" })).toHaveAttribute("href", "/ai");
  });

  it("shows empty state when no pending proposals", async () => {
    render(<ReviewMode />);
    await waitFor(() => {
      expect(screen.getByTestId("review-empty-state")).toBeTruthy();
      expect(screen.getByText(/Nessuna revisione in sospeso/i)).toBeTruthy();
    });
  });

  it("advances workflow from select to compare", async () => {
    addProposal({
      actionId: "rewrite",
      actionLabel: "Riscrivi",
      chapterId: "ch-1",
      selectionText: "Secondo originale.",
      selectionAnchor: null,
      preview: "Secondo rivisto.",
    });

    render(<ReviewMode />);

    await waitFor(() => {
      expect(screen.getByText("Capitolo 1 — Introduzione")).toBeTruthy();
    });

    fireEvent.click(screen.getByText("Capitolo 1 — Introduzione"));
    fireEvent.click(screen.getByRole("button", { name: "Confronta revisione" }));

    await waitFor(() => {
      expect(screen.getByText("Originale")).toBeTruthy();
      expect(screen.getByRole("button", { name: "Accetta tutto" })).toBeTruthy();
    });
  });

  it("exports dispatchOpenReview custom event", () => {
    const handler = vi.fn();
    window.addEventListener("thesisos:open-review", handler);
    dispatchOpenReview("ch-1");
    expect(handler).toHaveBeenCalledTimes(1);
    window.removeEventListener("thesisos:open-review", handler);
  });
});
