import { describe, expect, it, vi, afterEach } from "vitest";
import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import { WritingOutline } from "./WritingOutline";
import { WRITING_OUTLINE_STUB } from "./writingStub";

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
    render(<WritingOutline />);

    expect(screen.getByRole("navigation", { name: "Outline capitoli" })).toBeTruthy();
    expect(screen.getByText("Cap. 1 — Introduzione")).toBeTruthy();
    expect(screen.getByText("Cap. 5 — STIGMATA")).toBeTruthy();
    expect(
      screen.getByRole("link", { name: /Cap\. 2 — Quadro teorico/i })
    ).toHaveAttribute("href", "/writing/2");
  });

  it("marks active chapter with aria-current", () => {
    render(<WritingOutline activeChapterId="3" />);

    expect(
      screen.getByRole("link", { name: /Cap\. 3 — Metodologia/i })
    ).toHaveAttribute("aria-current", "page");
  });

  it("shows status labels for chapters", () => {
    render(<WritingOutline chapters={WRITING_OUTLINE_STUB} />);

    expect(screen.getByText("Approvato")).toBeTruthy();
    expect(screen.getByText("In revisione")).toBeTruthy();
    expect(screen.getAllByText("Bozza").length).toBeGreaterThan(0);
  });
});
