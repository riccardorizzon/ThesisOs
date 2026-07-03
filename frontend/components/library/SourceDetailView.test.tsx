import { describe, expect, it, vi, afterEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";
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

    expect(screen.getByRole("heading", { name: "L'opera d'arte" })).toBeTruthy();
    expect(screen.getByText("Walter Benjamin")).toBeTruthy();
    expect(screen.getByText(/Approvata/)).toBeTruthy();
    expect(screen.getByText("Aura")).toBeTruthy();
    expect(screen.getByText("Riproducibilità tecnica")).toBeTruthy();
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
});
