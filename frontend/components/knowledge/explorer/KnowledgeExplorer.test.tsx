import { describe, expect, it, vi, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";
import { KnowledgeExplorer } from "./KnowledgeExplorer";
import type { KnowledgeObjectEnvelope } from "@/lib/knowledgeTypes";

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
  }: {
    children: React.ReactNode;
    href: string;
  }) => <a href={href}>{children}</a>,
}));

afterEach(() => {
  cleanup();
});

const CONCEPTS: KnowledgeObjectEnvelope[] = [
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
      sources: 3,
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
    knowledge_state: "candidate",
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

describe("KnowledgeExplorer", () => {
  it("renders concept cards with lifecycle badges", () => {
    render(<KnowledgeExplorer concepts={CONCEPTS} />);
    expect(screen.getByRole("heading", { name: "Knowledge" })).toBeTruthy();
    expect(screen.getAllByText("STIGMATA").length).toBeGreaterThan(0);
    expect(screen.getAllByTestId("knowledge-state-linked").length).toBeGreaterThan(0);
  });

  it("hides candidates by default", () => {
    render(<KnowledgeExplorer concepts={CONCEPTS} />);
    expect(screen.queryByText("Aura")).toBeNull();
  });

  it("shows candidates when toggle enabled", () => {
    render(<KnowledgeExplorer concepts={CONCEPTS} />);
    fireEvent.click(
      screen.getByRole("checkbox", { name: /Mostra candidati/i })
    );
    expect(screen.getByText("Aura")).toBeTruthy();
  });

  it("links source counts to Sources module", () => {
    render(<KnowledgeExplorer concepts={CONCEPTS} />);
    expect(
      screen.getByRole("link", { name: /3 fonti in Sources/i })
    ).toHaveAttribute("href", "/sources");
  });

  it("shows empty state when corpus has no concepts", () => {
    render(<KnowledgeExplorer concepts={[]} />);
    expect(screen.getByTestId("knowledge-empty-state")).toBeTruthy();
    expect(screen.getByText(/Nessun concetto nel corpus/i)).toBeTruthy();
    expect(screen.queryByTestId("knowledge-filter-rail")).toBeNull();
  });
});
