import { describe, expect, it, vi } from "vitest";

import { KnowledgeObjectCard } from "@/components/knowledge/shared/KnowledgeObjectCard";
import type { KnowledgeObjectEnvelope } from "@/lib/knowledgeTypes";
import { render, screen } from "@testing-library/react";

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    prefetch,
    ...props
  }: {
    children: React.ReactNode;
    href: string;
    prefetch?: boolean;
  }) => (
    <a href={href} data-prefetch={String(prefetch)} {...props}>
      {children}
    </a>
  ),
}));

const SAMPLE: KnowledgeObjectEnvelope = {
  id: "aura",
  slug: "aura",
  type: "concept",
  title: "Aura",
  subtitle: "Benjamin — unicità dell'originale",
  summary: "Presenza unica dell'oggetto nel tempo e nello spazio.",
  confidence: "alta",
  knowledge_state: "validated",
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
  is_core: true,
};

describe("KnowledgeObjectCard", () => {
  it("renders envelope fields and lifecycle badge", () => {
    render(<KnowledgeObjectCard object={SAMPLE} />);
    expect(screen.getByText("Aura")).toBeInTheDocument();
    expect(screen.getByText("Benjamin — unicità dell'originale")).toBeInTheDocument();
    expect(screen.getByTestId("knowledge-state-validated")).toHaveTextContent("Validato");
    expect(screen.getByTestId("confidence-alta")).toHaveTextContent("Alta");
    expect(screen.getByText("Core")).toBeInTheDocument();
    expect(screen.getByText("1 fonti")).toBeInTheDocument();
  });

  it("disables speculative prefetch for high-cardinality cards", () => {
    render(<KnowledgeObjectCard object={SAMPLE} href="/knowledge/aura" />);
    expect(screen.getByRole("link")).toHaveAttribute("data-prefetch", "false");
  });
});
