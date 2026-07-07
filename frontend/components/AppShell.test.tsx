import { describe, expect, it, vi, afterEach, beforeEach } from "vitest";
import { render, screen, cleanup, waitFor } from "@testing-library/react";
import { AppShell } from "./AppShell";
import { DEFAULT_PROJECT_ID } from "@/lib/projectContext";
import {
  _resetProposalQueueForTests,
  addProposal,
} from "@/lib/proposalQueue";
import { chapterClient } from "@/lib/chapterClient";

vi.mock("next/navigation", () => ({
  usePathname: () => "/writing",
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
  }),
}));

vi.mock("@/lib/projectsClient", () => ({
  listProjects: vi.fn().mockResolvedValue([
    {
      id: "thesis-agent",
      display_name: "Tesi di laurea",
      created_at: "2026-07-01T00:00:00Z",
    },
  ]),
  createProject: vi.fn(),
}));

vi.mock("@/lib/chapterClient", () => ({
  chapterClient: {
    list: vi.fn().mockResolvedValue([
      {
        id: "1",
        parent_id: null,
        order_index: 0,
        title: "Cap. 1",
        status: "review",
        content_md: null,
        summary: null,
        word_count: 0,
        version: 1,
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
      },
    ]),
  },
}));

beforeEach(() => {
  _resetProposalQueueForTests();
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

afterEach(() => {
  cleanup();
  _resetProposalQueueForTests();
});

describe("AppShell", () => {
  it("renders primary navigation per ADR-0036", async () => {
    render(
      <AppShell>
        <div>Content</div>
      </AppShell>
    );
    const nav = screen.getByRole("navigation", { name: "Primary" });
    expect(nav).toBeTruthy();
    for (const label of ["Home", "Research", "Writing", "Sources", "Knowledge"]) {
      expect(screen.getByRole("link", { name: label })).toBeTruthy();
    }
    expect(screen.getByRole("link", { name: "Settings" })).toBeTruthy();
  });

  it("renders project switcher and breadcrumbs", async () => {
    render(
      <AppShell>
        <div>Content</div>
      </AppShell>
    );
    await waitFor(() => {
      expect(screen.getByText("Tesi di laurea")).toBeTruthy();
    });
    const breadcrumb = screen.getByRole("navigation", { name: "Breadcrumb" });
    expect(breadcrumb).toBeTruthy();
    expect(
      breadcrumb.querySelector('[aria-current="page"]')?.textContent
    ).toBe("Writing");
  });

  it("renders optional right panel slot", () => {
    render(
      <AppShell rightPanel={<div>AI Panel</div>}>
        <div>Content</div>
      </AppShell>
    );
    expect(screen.getByRole("complementary", { name: "Panel" })).toBeTruthy();
    expect(screen.getByText("AI Panel")).toBeTruthy();
  });

  it("omits right panel when not provided", () => {
    render(
      <AppShell>
        <div>Content</div>
      </AppShell>
    );
    expect(screen.queryByRole("complementary", { name: "Panel" })).toBeNull();
  });

  it("shows command palette trigger with ⌘K hint", () => {
    render(
      <AppShell>
        <div>Content</div>
      </AppShell>
    );
    const trigger = screen.getByTestId("command-palette-trigger");
    expect(trigger).toBeTruthy();
    expect(trigger.textContent).toContain("⌘K");
  });

  it("shows writing status dot and review pending count", async () => {
    addProposal({
      actionId: "expand",
      actionLabel: "Espandi",
      chapterId: "1",
      selectionText: null,
      selectionAnchor: null,
      preview: "Anteprima",
    });

    render(
      <AppShell>
        <div>Content</div>
      </AppShell>
    );

    await vi.waitFor(() => {
      expect(screen.getByTestId("nav-badge-writing")).toBeTruthy();
      expect(screen.getByTestId("nav-review-pending")).toBeTruthy();
    });
    expect(vi.mocked(chapterClient.list)).toHaveBeenCalled();
  });
});
