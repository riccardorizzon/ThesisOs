import { describe, expect, it } from "vitest";

import { KnowledgeObjectCard } from "@/components/knowledge/shared/KnowledgeObjectCard";
import type { KnowledgeObjectEnvelope } from "@/lib/knowledgeTypes";
import { render, screen } from "@testing-library/react";

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
});
