import { describe, expect, it, vi, afterEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";
import { KnowledgeView } from "./KnowledgeView";
import type { KnowledgeObjectEnvelope } from "@/lib/knowledgeTypes";

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

const TEST_CONCEPTS: KnowledgeObjectEnvelope[] = [
  {
    id: "stigmata",
    slug: "stigmata",
    type: "concept",
    title: "STIGMATA",
    subtitle: "Framework centrale",
    summary: "Segno percettivo",
    confidence: "alta",
    knowledge_state: "linked",
    linked_counts: {
      sources: 2,
      chapters: 0,
      concepts: 0,
      decisions: 0,
      authors: 0,
      citations: 0,
    },
    created_by: "operatore",
    proposal_state: "nessuna",
    is_core: true,
  },
  {
    id: "aura",
    slug: "aura",
    type: "concept",
    title: "Aura",
    subtitle: "Benjamin",
    summary: "Presenza unica",
    confidence: "alta",
    knowledge_state: "linked",
    linked_counts: {
      sources: 1,
      chapters: 0,
      concepts: 0,
      decisions: 0,
      authors: 0,
      citations: 0,
    },
    created_by: "operatore",
    proposal_state: "nessuna",
    is_core: false,
  },
];

afterEach(() => {
  cleanup();
});

describe("KnowledgeView", () => {
  it("renders concept cards and cross-link to Sources", () => {
    render(<KnowledgeView concepts={TEST_CONCEPTS} />);

    expect(screen.getByRole("heading", { name: "Knowledge" })).toBeTruthy();
    expect(screen.getByText("STIGMATA")).toBeTruthy();
    expect(screen.getByText("Aura")).toBeTruthy();
    expect(screen.getByRole("link", { name: "Sources" })).toHaveAttribute(
      "href",
      "/sources"
    );
  });

  it("links each concept card to detail route", () => {
    render(<KnowledgeView concepts={TEST_CONCEPTS} />);

    expect(screen.getByRole("link", { name: /STIGMATA/i })).toHaveAttribute(
      "href",
      "/knowledge/stigmata"
    );
  });
});
