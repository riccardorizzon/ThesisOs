import { describe, expect, it, afterEach, vi, beforeEach } from "vitest";
import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import { FIXTURE_CONTEXT_PACKET } from "@/lib/fixtures/contextFixture";
import { FIXTURE_WRITING_OUTLINE } from "@/lib/fixtures/writingFixture";
import { WritingWorkspace } from "./WritingWorkspace";

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
  }),
  useSearchParams: () => new URLSearchParams("section=intro"),
}));

vi.mock("@/lib/documentClient", () => ({
  documentClient: {
    list: vi.fn().mockResolvedValue([]),
    get: vi.fn().mockResolvedValue({
      id: "doc-1",
      title: "Test",
      status: "parsed",
      author: null,
      source_type: "pdf",
      original_filename: null,
      gcs_uri: null,
      page_count: null,
      language: null,
      version: 1,
      parser: null,
      parsed_at: null,
      chunk_count: 10,
      error_message: null,
      metadata: {},
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    }),
  },
  documentDisplayTitle: (d: { title?: string | null }) => d.title ?? "(untitled)",
}));

vi.mock("@/lib/chapterClient", () => ({
  chapterClient: {
    list: vi.fn().mockResolvedValue([]),
    get: vi.fn().mockResolvedValue({
      id: "1",
      parent_id: null,
      order_index: 0,
      title: "Cap. 1",
      status: "draft",
      content_md: "# Test",
      summary: null,
      word_count: 1,
      version: 1,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    }),
    update: vi.fn(),
    create: vi.fn(),
  },
  ChapterApiError: class ChapterApiError extends Error {
    status = 409;
    code = "write_conflict";
  },
}));

afterEach(() => {
  cleanup();
});

describe("WritingWorkspace", () => {
  beforeEach(() => {
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: vi.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      })),
    });
  });

  it("renders three-panel shell with outline, editor, and AI panel", () => {
    render(<WritingWorkspace chapterId="1" contextPacket={FIXTURE_CONTEXT_PACKET} />);

    expect(screen.getByTestId("writing-workspace")).toBeTruthy();
    expect(screen.getByRole("navigation", { name: "Outline capitoli" })).toBeTruthy();
    expect(screen.getByRole("region", { name: "Editor Markdown" })).toBeTruthy();
    expect(
      screen.getByRole("complementary", { name: "Pannello laterale scrittura" })
    ).toBeTruthy();
  });

  it("highlights active chapter in outline", () => {
    render(
      <WritingWorkspace
        chapterId="4"
        contextPacket={FIXTURE_CONTEXT_PACKET}
        chapters={FIXTURE_WRITING_OUTLINE}
      />
    );

    expect(
      screen.getByRole("link", { name: /Cap\. 4 — Analisi/i })
    ).toHaveAttribute("aria-current", "page");
  });

  it("uses panel width tokens on outline and rail", () => {
    render(<WritingWorkspace chapterId="2" contextPacket={FIXTURE_CONTEXT_PACKET} />);

    const outlinePanel = document.getElementById("writing-outline-panel");
    const railPanel = document.getElementById("writing-rail-panel");

    expect(outlinePanel?.className).toMatch(/lg:w-outline/);
    expect(railPanel?.className).toMatch(/lg:w-rail/);
  });

  it("shows read-only banner below 768px", () => {
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: vi.fn().mockImplementation((query: string) => ({
        matches: query.includes("max-width"),
        media: query,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      })),
    });

    render(<WritingWorkspace chapterId="1" contextPacket={FIXTURE_CONTEXT_PACKET} />);
    expect(screen.getByTestId("writing-readonly-banner")).toBeTruthy();
  });

  it("toggles outline panel on small screens", () => {
    render(<WritingWorkspace chapterId="2" contextPacket={FIXTURE_CONTEXT_PACKET} />);

    const outlineToggle = screen.getByRole("button", { name: "Outline" });
    const outlinePanel = document.getElementById("writing-outline-panel");

    expect(outlinePanel?.className).toMatch(/hidden/);

    fireEvent.click(outlineToggle);
    expect(outlinePanel?.className).toMatch(/block/);
    expect(outlineToggle).toHaveAttribute("aria-pressed", "true");
  });

  it("renders linked sources footer with count", () => {
    render(<WritingWorkspace chapterId="3" contextPacket={FIXTURE_CONTEXT_PACKET} />);
    const footer = screen.getByTestId("linked-sources-footer");
    expect(footer).toBeTruthy();
    expect(footer).toHaveTextContent(/Fonti collegate \(\d+\)/);
  });

  it("shows create-chapter empty state when no chapters", async () => {
    render(<WritingWorkspace contextPacket={FIXTURE_CONTEXT_PACKET} />);

    expect(await screen.findByTestId("writing-chapters-empty")).toBeTruthy();
    expect(screen.getByTestId("writing-create-chapter-cta")).toHaveTextContent("Crea capitolo");
    expect(screen.getByTestId("writing-outline-add-chapter")).toBeTruthy();
  });
});
