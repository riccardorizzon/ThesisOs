import { describe, expect, it, vi, afterEach } from "vitest";
import { render, screen, cleanup, fireEvent, act } from "@testing-library/react";
import { SourcesView } from "./SourcesView";
import type { LibrarySource } from "@/lib/libraryTypes";

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    className,
    ...rest
  }: {
    children: React.ReactNode;
    href: string;
    className?: string;
    [key: string]: unknown;
  }) => (
    <a href={href} className={className} {...rest}>
      {children}
    </a>
  ),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh: vi.fn() }),
}));

const TEST_SOURCES: LibrarySource[] = [
  {
    id: "a",
    title: "Fonte approvata",
    subtitle: "Autore A",
    meta: "2020",
    status: "approvata",
    relatedConceptIds: ["aura"],
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
  it("shows add-source CTA in header linking to upload", () => {
    render(<SourcesView sources={TEST_SOURCES} />);

    const cta = screen.getByTestId("sources-add-source-cta");
    expect(cta).toHaveAttribute("href", "/sources/upload");
    expect(cta).toHaveTextContent("Aggiungi fonte");
  });

  it("shows actionable empty state with add-source CTA", () => {
    render(<SourcesView sources={[]} />);

    expect(screen.getByTestId("sources-corpus-empty")).toBeTruthy();
    expect(screen.getByTestId("sources-add-source-cta")).toHaveAttribute(
      "href",
      "/sources/upload"
    );
  });

  it("renders enriched source cards and cross-link to Knowledge", () => {
    render(<SourcesView sources={TEST_SOURCES} />);

    expect(screen.getByRole("heading", { name: "Sources" })).toBeTruthy();
    expect(screen.getByText("Fonte approvata")).toBeTruthy();
    expect(screen.getByText("Fonte candidata")).toBeTruthy();
    expect(screen.queryByText("Fonte esclusa")).toBeNull();
    expect(screen.getAllByRole("link", { name: "Knowledge" }).length).toBeGreaterThan(0);
    expect(screen.getByTestId("sources-filter-rail")).toBeTruthy();
  });

  it("shows concept relationship chip linking to Knowledge", () => {
    render(<SourcesView sources={TEST_SOURCES} />);
    const chip = screen.getByRole("link", { name: "aura" });
    expect(chip).toHaveAttribute("href", "/knowledge/aura");
  });

  it("filters sources by knowledge state", () => {
    render(<SourcesView sources={TEST_SOURCES} />);

    fireEvent.change(screen.getByLabelText("Filtra per stato knowledge"), {
      target: { value: "candidate" },
    });
    expect(screen.getByText("Fonte candidata")).toBeTruthy();
    expect(screen.queryByText("Fonte approvata")).toBeNull();
  });

  it("links each source card to detail route", () => {
    render(<SourcesView sources={TEST_SOURCES} />);

    expect(
      screen.getByRole("link", { name: /Fonte approvata/i })
    ).toHaveAttribute("href", "/sources/a");
  });

  it("shows sticky return-to-writing pill when chapter context set", () => {
    render(<SourcesView sources={TEST_SOURCES} chapterContext="ch-3" />);

    expect(screen.getByRole("link", { name: "Torna a Scrittura" })).toHaveAttribute(
      "href",
      "/writing/ch-3"
    );
  });

  it("debounces corpus search input", async () => {
    vi.useFakeTimers();
    render(<SourcesView sources={TEST_SOURCES} />);

    fireEvent.change(screen.getByTestId("sources-search-input"), {
      target: { value: "approvata" },
    });

    expect(screen.getByText("Fonte candidata")).toBeTruthy();

    await act(async () => {
      vi.advanceTimersByTime(200);
    });

    expect(screen.getByText("Fonte approvata")).toBeTruthy();
    expect(screen.queryByText("Fonte candidata")).toBeNull();
    vi.useRealTimers();
  });
});
