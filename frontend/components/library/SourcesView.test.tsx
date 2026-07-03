import { describe, expect, it, vi, afterEach } from "vitest";
import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import { SourcesView } from "./SourcesView";
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

const TEST_SOURCES: LibrarySource[] = [
  {
    id: "a",
    title: "Fonte approvata",
    subtitle: "Autore A",
    meta: "2020",
    status: "approvata",
    relatedConceptIds: [],
  },
  {
    id: "b",
    title: "Fonte candidata",
    subtitle: "Autore B",
    status: "candidata",
    relatedConceptIds: [],
  },
  {
    id: "c",
    title: "Fonte esclusa",
    status: "esclusa",
    relatedConceptIds: [],
  },
];

afterEach(() => {
  cleanup();
});

describe("SourcesView", () => {
  it("renders source cards and cross-link to Knowledge", () => {
    render(<SourcesView sources={TEST_SOURCES} />);

    expect(screen.getByRole("heading", { name: "Sources" })).toBeTruthy();
    expect(screen.getByText("Fonte approvata")).toBeTruthy();
    expect(screen.getByText("Fonte candidata")).toBeTruthy();
    expect(screen.getByText("Fonte esclusa")).toBeTruthy();
    expect(screen.getByRole("link", { name: "Knowledge" })).toHaveAttribute(
      "href",
      "/knowledge"
    );
  });

  it("shows filter bar with status options", () => {
    render(<SourcesView sources={TEST_SOURCES} />);

    expect(screen.getByRole("group", { name: /Filtra per stato/i })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Tutte" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Candidata" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Approvata" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Esclusa" })).toBeTruthy();
  });

  it("filters sources by status", () => {
    render(<SourcesView sources={TEST_SOURCES} />);

    fireEvent.click(screen.getByRole("button", { name: "Approvata" }));
    expect(screen.getByText("Fonte approvata")).toBeTruthy();
    expect(screen.queryByText("Fonte candidata")).toBeNull();
    expect(screen.queryByText("Fonte esclusa")).toBeNull();
  });

  it("links each source card to detail route", () => {
    render(<SourcesView sources={TEST_SOURCES} />);

    expect(
      screen.getByRole("link", { name: /Fonte approvata/i })
    ).toHaveAttribute("href", "/sources/a");
  });
});
