import { describe, expect, it, vi, afterEach, beforeAll } from "vitest";
import { render, screen, fireEvent, cleanup, waitFor } from "@testing-library/react";
import { ResearchInspectorRail } from "./ResearchInspectorRail";
import type { KnowledgeGraphResponse } from "@/lib/knowledgeTypes";

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

vi.mock("@/lib/knowledgeClient", () => ({
  getKnowledgeObject: vi.fn(async (slug: string) => ({
    id: slug,
    slug,
    type: "concept",
    title: slug === "aura" ? "Aura" : slug,
    confidence: "alta",
    knowledge_state: "validated",
    linked_counts: {
      sources: 1,
      chapters: 1,
      concepts: 2,
      decisions: 0,
      authors: 1,
      citations: 0,
    },
    created_by: "operatore",
    proposal_state: "nessuna",
    is_core: true,
    summary: "Riepilogo concetto di test.",
  })),
}));

const SAMPLE_GRAPH: KnowledgeGraphResponse = {
  schema_version: 1,
  focus_slug: "aura",
  depth: 2,
  view_mode: "graph",
  nodes: [
    {
      id: "aura",
      slug: "aura",
      title: "Aura",
      knowledge_state: "validated",
      is_core: true,
      degree: 2,
    },
    {
      id: "stigmata",
      slug: "stigmata",
      title: "STIGMATA",
      knowledge_state: "referenced",
      is_core: false,
      degree: 3,
    },
  ],
  edges: [{ source: "aura", target: "stigmata", relation: "related" }],
  limits: {
    default_visible: 80,
    soft_limit: 150,
    hard_limit: 300,
    visible_count: 2,
    total_in_scope: 2,
    truncated: false,
    force_list_view: false,
    show_performance_banner: false,
  },
};

afterEach(() => {
  cleanup();
});

describe("ResearchInspectorRail", () => {
  it("shows empty state when nothing selected", () => {
    render(<ResearchInspectorRail selectedSlugs={[]} graph={SAMPLE_GRAPH} />);
    expect(screen.getByTestId("canvas-inspector-empty")).toBeTruthy();
  });

  it("shows batch summary for multi-select", () => {
    render(
      <ResearchInspectorRail selectedSlugs={["aura", "stigmata"]} graph={SAMPLE_GRAPH} />
    );
    expect(screen.getByTestId("canvas-inspector-multi")).toHaveTextContent("2 nodi selezionati");
  });

  it("populates tabs for single selection", async () => {
    render(<ResearchInspectorRail selectedSlugs={["aura"]} graph={SAMPLE_GRAPH} />);
    await waitFor(() => {
      expect(screen.getByTestId("canvas-inspector-dettaglio")).toBeTruthy();
    });
    fireEvent.click(screen.getByRole("tab", { name: "Collegamenti" }));
    expect(screen.getByTestId("canvas-inspector-collegamenti")).toBeTruthy();
    fireEvent.click(screen.getByRole("tab", { name: "Azioni" }));
    expect(screen.getByRole("link", { name: "Apri Explain" })).toHaveAttribute(
      "href",
      "/knowledge/aura"
    );
  });
});
