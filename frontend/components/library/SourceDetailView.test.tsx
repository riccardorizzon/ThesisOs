import { describe, expect, it, vi, afterEach } from "vitest";
import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import { SourceDetailView } from "./SourceDetailView";
import type { LibrarySource } from "@/lib/libraryStub";

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

const TEST_SOURCE: LibrarySource = {
  id: "benjamin-opera-arte",
  title: "L'opera d'arte",
  subtitle: "Walter Benjamin",
  meta: "1936",
  status: "approvata",
  relatedConceptIds: ["aura", "riproducibilita"],
};

afterEach(() => {
  cleanup();
});

describe("SourceDetailView", () => {
  it("renders source metadata and related concepts", () => {
    render(<SourceDetailView source={TEST_SOURCE} />);

    expect(
      screen.getByRole("heading", {
        name: /L'opera d'arte/i,
      })
    ).toBeTruthy();
    expect(screen.getByText("Walter Benjamin")).toBeTruthy();
    expect(screen.getAllByText(/Approvata/).length).toBeGreaterThan(0);
    expect(screen.getAllByText("Aura").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Riproducibilità tecnica").length).toBeGreaterThan(0);
    expect(screen.getByRole("link", { name: /← Sources/i })).toHaveAttribute(
      "href",
      "/sources"
    );
  });

  it("links related concepts to knowledge detail", () => {
    render(<SourceDetailView source={TEST_SOURCE} />);

    expect(screen.getByRole("link", { name: /Aura/i })).toHaveAttribute(
      "href",
      "/knowledge/aura"
    );
  });

  it("shows Collega al capitolo when chapter context provided", () => {
    localStorage.clear();
    render(<SourceDetailView source={TEST_SOURCE} chapterContext="cap-2" />);

    expect(screen.getByTestId("link-to-chapter-btn")).toHaveTextContent(
      "Collega al capitolo"
    );
    fireEvent.click(screen.getByTestId("link-to-chapter-btn"));
    expect(screen.getByTestId("link-success")).toBeTruthy();
  });
});
