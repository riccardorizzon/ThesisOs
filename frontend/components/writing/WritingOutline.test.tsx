import { describe, expect, it, vi, afterEach } from "vitest";
import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import { WritingOutline } from "./WritingOutline";
import { FIXTURE_WRITING_OUTLINE } from "@/lib/fixtures/writingFixture";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}));

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    className,
    "aria-current": ariaCurrent,
  }: {
    children: React.ReactNode;
    href: string;
    className?: string;
    "aria-current"?: "page" | boolean;
  }) => (
    <a href={href} className={className} aria-current={ariaCurrent}>
      {children}
    </a>
  ),
}));

afterEach(() => {
  cleanup();
});

describe("WritingOutline", () => {
  it("renders chapter list with links", () => {
    render(<WritingOutline chapters={FIXTURE_WRITING_OUTLINE} />);

    expect(screen.getByRole("navigation", { name: "Outline capitoli" })).toBeTruthy();
    expect(screen.getByText("Cap. 1 — Introduzione")).toBeTruthy();
    expect(
      screen.getByRole("link", { name: /Cap\. 2 — Quadro teorico/i })
    ).toHaveAttribute("href", "/writing/2");
  });

  it("marks active chapter with aria-current", () => {
    render(<WritingOutline chapters={FIXTURE_WRITING_OUTLINE} activeChapterId="3" />);

    expect(
      screen.getByRole("link", { name: /Cap\. 3 — Metodologia/i })
    ).toHaveAttribute("aria-current", "page");
  });

  it("shows StatusBadge for chapter lifecycle", () => {
    render(<WritingOutline chapters={FIXTURE_WRITING_OUTLINE} />);

    expect(screen.getByTestId("status-badge-approved")).toBeTruthy();
    expect(screen.getByTestId("status-badge-review")).toBeTruthy();
    expect(screen.getAllByTestId("status-badge-draft").length).toBeGreaterThan(0);
  });

  it("filters chapters by status segment", () => {
    render(<WritingOutline chapters={FIXTURE_WRITING_OUTLINE} />);

    fireEvent.click(screen.getByRole("button", { name: "Da revisionare" }));
    expect(screen.getByText("Cap. 2 — Quadro teorico")).toBeTruthy();
    expect(screen.queryByText("Cap. 1 — Introduzione")).toBeNull();
  });

  it("renders section links with ?section= query", () => {
    render(
      <WritingOutline
        chapters={FIXTURE_WRITING_OUTLINE}
        activeChapterId="3"
        activeSectionId="metodo"
        sections={[
          { id: "metodo", label: "Metodo", level: 2, lineIndex: 2 },
        ]}
      />
    );

    expect(screen.getByRole("link", { name: "Metodo" })).toHaveAttribute(
      "href",
      "/writing/3?section=metodo"
    );
  });

  it("shows add-chapter control when onChapterCreated is provided", () => {
    render(
      <WritingOutline
        chapters={FIXTURE_WRITING_OUTLINE}
        onChapterCreated={vi.fn()}
      />
    );

    expect(screen.getByTestId("writing-outline-add-chapter")).toBeTruthy();
  });
});
