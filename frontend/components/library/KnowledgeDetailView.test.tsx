import { describe, expect, it, vi, afterEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";
import { KnowledgeDetailView } from "./KnowledgeDetailView";
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

const TEST_CONCEPT: LibraryConcept = {
  id: "stigmata",
  title: "STIGMATA",
  subtitle: "Framework centrale",
  definition: "Segno percettivo culturale.",
  relatedSourceIds: ["benjamin-opera-arte", "hollander-sex-suits"],
};

afterEach(() => {
  cleanup();
});

describe("KnowledgeDetailView", () => {
  it("renders concept definition and related sources", () => {
    render(<KnowledgeDetailView concept={TEST_CONCEPT} />);

    expect(screen.getByRole("heading", { name: "STIGMATA" })).toBeTruthy();
    expect(screen.getByText("Segno percettivo culturale.")).toBeTruthy();
    expect(
      screen.getByText("L'opera d'arte nell'epoca della riproducibilità tecnica")
    ).toBeTruthy();
    expect(screen.getByText("Sex and Suits")).toBeTruthy();
    expect(screen.getByRole("link", { name: /← Knowledge/i })).toHaveAttribute(
      "href",
      "/knowledge"
    );
  });

  it("links related sources to source detail", () => {
    render(<KnowledgeDetailView concept={TEST_CONCEPT} />);

    expect(
      screen.getByRole("link", {
        name: /L'opera d'arte nell'epoca della riproducibilità tecnica/i,
      })
    ).toHaveAttribute("href", "/sources/benjamin-opera-arte");
  });
});
