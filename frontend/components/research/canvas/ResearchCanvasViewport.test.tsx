import { describe, expect, it, vi, afterEach, beforeAll } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";
import { ResearchCanvasViewport } from "./ResearchCanvasViewport";
import type { KnowledgeGraphResponse } from "@/lib/knowledgeTypes";
import {
  layoutCanvasNodes,
  nodeRadius,
  truncateLabel,
  visibleWorldBounds,
  isNodeVisible,
} from "@/lib/canvasLayout";

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
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
      id: "riproducibilita",
      slug: "riproducibilita",
      title: "Riproducibilità tecnica",
      knowledge_state: "linked",
      is_core: false,
      degree: 1,
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
  edges: [
    { source: "aura", target: "riproducibilita", relation: "supports" },
    { source: "aura", target: "stigmata", relation: "related" },
  ],
  limits: {
    default_visible: 80,
    soft_limit: 150,
    hard_limit: 300,
    visible_count: 3,
    total_in_scope: 7,
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
});

describe("canvasLayout", () => {
  it("places focus node at origin", () => {
    const layout = layoutCanvasNodes(SAMPLE_GRAPH);
    expect(layout.get("aura")).toEqual({ slug: "aura", x: 0, y: 0 });
  });

  it("uses larger radius for core concepts", () => {
    expect(nodeRadius(SAMPLE_GRAPH.nodes[0])).toBe(32);
    expect(nodeRadius(SAMPLE_GRAPH.nodes[1])).toBe(24);
  });

  it("truncates long labels", () => {
    expect(truncateLabel("Short")).toBe("Short");
    expect(truncateLabel("A".repeat(40)).length).toBeLessThanOrEqual(32);
  });

  it("culls off-screen nodes", () => {
    const bounds = visibleWorldBounds(800, 600, { x: 400, y: 300, scale: 1 });
    expect(isNodeVisible(0, 0, 32, bounds)).toBe(true);
    expect(isNodeVisible(5000, 5000, 32, bounds)).toBe(false);
  });
});

describe("ResearchCanvasViewport", () => {
  it("renders viewport with concept nodes", () => {
    render(<ResearchCanvasViewport graph={SAMPLE_GRAPH} />);
    expect(screen.getByTestId("research-canvas-viewport")).toBeTruthy();
    expect(screen.getByTestId("canvas-node-aura")).toBeTruthy();
    expect(screen.getByTestId("canvas-node-riproducibilita")).toBeTruthy();
  });

  it("selects node on click", () => {
    render(<ResearchCanvasViewport graph={SAMPLE_GRAPH} />);
    fireEvent.click(screen.getByTestId("canvas-node-stigmata"));
    expect(screen.getByTestId("canvas-selection-chip")).toHaveTextContent("STIGMATA");
  });

  it("renders typed edges", () => {
    render(<ResearchCanvasViewport graph={SAMPLE_GRAPH} />);
    expect(screen.getByTestId("canvas-edge-aura-riproducibilita")).toBeTruthy();
  });
});
