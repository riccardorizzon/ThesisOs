import { describe, expect, it, vi, afterEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";
import { KnowledgeView } from "./KnowledgeView";
import type { LibraryConcept } from "@/lib/libraryStub";

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

const TEST_CONCEPTS: LibraryConcept[] = [
  {
    id: "stigmata",
    title: "STIGMATA",
    subtitle: "Framework centrale",
    meta: "2 fonti",
    relatedSourceIds: ["a", "b"],
  },
  {
    id: "aura",
    title: "Aura",
    subtitle: "Benjamin",
    relatedSourceIds: ["a"],
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
