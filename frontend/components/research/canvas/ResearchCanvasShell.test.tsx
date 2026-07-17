import { describe, expect, it, vi, afterEach, beforeAll } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";
import { ResearchCanvasShell } from "./ResearchCanvasShell";
import type { KnowledgeGraphResponse } from "@/lib/knowledgeTypes";

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("@/lib/contextLoadClient", () => ({
  loadContextClient: vi.fn(async () => ({
    schema_version: "1",
    project_context: {
      project_id: "thesis-agent",
      product_id: "thesisos",
      workspace_id: "default",
      session_id: "default",
    },
    presentation: { surface: "research" },
    project: { title: "Tesi", phase: "writing", progress_pct: 10 },
    concepts: [{ id: "aura", slug: "aura", title: "Aura" }],
    relevant_sources: [],
    decisions: [],
    definitions: [],
    citations_available: [],
    corpus_constraints: [],
    writing_rules: [],
    memory_proposals_pending: 0,
    recent_activity: [],
    token_budget: 8000,
  })),
}));

vi.mock("@/lib/knowledgeClient", () => ({
  listKnowledgeObjects: vi.fn(async () => ({
    objects: [
      {
        id: "aura",
        slug: "aura",
        type: "concept",
        title: "Aura",
        confidence: "alta",
        knowledge_state: "validated",
        linked_counts: {
          sources: 1,
          chapters: 0,
          concepts: 1,
          decisions: 0,
          authors: 0,
          citations: 0,
        },
        created_by: "operatore",
        proposal_state: "nessuna",
        is_core: true,
      },
    ],
    total: 1,
  })),
  getKnowledgeObject: vi.fn(async (slug: string) => ({
    id: slug,
    slug,
    type: "concept",
    title: "Aura",
    confidence: "alta",
    knowledge_state: "validated",
    linked_counts: {
      sources: 1,
      chapters: 0,
      concepts: 1,
      decisions: 0,
      authors: 0,
      citations: 0,
    },
    created_by: "operatore",
    proposal_state: "nessuna",
    is_core: true,
    summary: "Test",
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
    {
      id: "mito",
      slug: "mito",
      title: "Mito",
      knowledge_state: "validated",
      is_core: false,
      degree: 1,
    },
  ],
  edges: [
    { source: "aura", target: "stigmata", relation: "related" },
    { source: "aura", target: "mito", relation: "related" },
  ],
  limits: {
    default_visible: 80,
    soft_limit: 150,
    hard_limit: 300,
    visible_count: 3,
    total_in_scope: 3,
    truncated: false,
    force_list_view: false,
    show_performance_banner: false,
  },
};

afterEach(() => {
  cleanup();
});

beforeAll(() => {
  class ResizeObserverMock {
    private callback: ResizeObserverCallback;

    constructor(callback: ResizeObserverCallback) {
      this.callback = callback;
    }

    observe(element: Element) {
      this.callback(
        [
          {
            contentRect: {
              width: element.clientWidth || 800,
              height: element.clientHeight || 560,
            },
          } as ResizeObserverEntry,
        ],
        this as unknown as ResizeObserver
      );
    }

    unobserve() {}
    disconnect() {}
  }
  vi.stubGlobal("ResizeObserver", ResizeObserverMock);
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: true,
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    })),
  });
});

describe("ResearchCanvasShell", () => {
  it("renders three-region shell with header and action bar", () => {
    render(<ResearchCanvasShell graph={SAMPLE_GRAPH} focus="aura" />);
    expect(screen.getByTestId("research-canvas-shell")).toBeTruthy();
    expect(screen.getByTestId("canvas-header-bar")).toBeTruthy();
    expect(screen.getByTestId("canvas-three-region-shell")).toBeTruthy();
    expect(screen.getByTestId("canvas-lens-slot")).toBeTruthy();
    expect(screen.getByTestId("canvas-inspector-slot")).toBeTruthy();
    expect(screen.getByTestId("canvas-action-bar")).toBeTruthy();
  });

  it("enables lens dropdown and lens rail", () => {
    render(<ResearchCanvasShell graph={SAMPLE_GRAPH} />);
    expect(screen.getByTestId("canvas-lens-dropdown")).not.toBeDisabled();
    expect(screen.getByTestId("canvas-lens-rail")).toBeTruthy();
  });

  it("renders serendipity strip with suggestions", () => {
    render(<ResearchCanvasShell graph={SAMPLE_GRAPH} />);
    expect(screen.getByTestId("canvas-serendipity-strip")).toBeTruthy();
  });

  it("clears selection on Escape", () => {
    render(<ResearchCanvasShell graph={SAMPLE_GRAPH} focus="aura" />);
    expect(screen.getByTestId("canvas-selection-count")).toHaveTextContent("1 selezionato");
    fireEvent.keyDown(window, { key: "Escape" });
    expect(screen.getByTestId("canvas-selection-count")).toHaveTextContent("Nessuna selezione");
  });

  it("adds selection to basket from action bar", () => {
    sessionStorage.clear();
    render(<ResearchCanvasShell graph={SAMPLE_GRAPH} focus="aura" />);
    fireEvent.click(screen.getByTestId("canvas-add-basket-button"));
    expect(screen.getByTestId("canvas-basket-badge")).toHaveTextContent("Basket 1");
  });

  it("shows desktop-required message below 1024px", () => {
    const matchMedia = vi.fn().mockImplementation((query: string) => ({
      matches: false,
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }));
    vi.stubGlobal("matchMedia", matchMedia);

    render(<ResearchCanvasShell graph={SAMPLE_GRAPH} />);
    expect(screen.getByTestId("canvas-desktop-required")).toBeTruthy();
  });
});
