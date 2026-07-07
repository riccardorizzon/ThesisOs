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

  it("disables lens and basket controls until later waves", () => {
    render(<ResearchCanvasShell graph={SAMPLE_GRAPH} />);
    expect(screen.getByTestId("canvas-lens-dropdown")).toBeDisabled();
    expect(screen.getByTestId("canvas-basket-badge")).toBeDisabled();
    expect(screen.getByTestId("canvas-writing-handoff-button")).toBeDisabled();
  });

  it("clears selection on Escape", () => {
    render(<ResearchCanvasShell graph={SAMPLE_GRAPH} focus="aura" />);
    expect(screen.getByTestId("canvas-selection-count")).toHaveTextContent("1 selezionato");
    fireEvent.keyDown(window, { key: "Escape" });
    expect(screen.getByTestId("canvas-selection-count")).toHaveTextContent("Nessuna selezione");
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
