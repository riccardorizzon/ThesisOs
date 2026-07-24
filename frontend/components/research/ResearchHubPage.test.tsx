import { describe, expect, it, vi, afterEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";
import { ResearchHubPage } from "./ResearchHubPage";

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
  }) => (
    <a href={href} className={className} {...rest}>
      {children}
    </a>
  ),
}));

afterEach(() => {
  cleanup();
});

describe("ResearchHubPage", () => {
  it("enables canvas card when concepts exist", () => {
    render(<ResearchHubPage conceptCount={3} />);
    expect(screen.getAllByTestId("mode-card-enabled")).toHaveLength(1);
    expect(screen.getByRole("link", { name: /Apri mappa/i })).toHaveAttribute(
      "href",
      "/research/canvas"
    );
    expect(screen.queryByText("Esplorazione guidata")).not.toBeInTheDocument();
    expect(screen.queryByText(/trail guidato/i)).not.toBeInTheDocument();
  });

  it("disables canvas card when no concepts", () => {
    render(<ResearchHubPage conceptCount={0} />);
    expect(screen.getByTestId("mode-card-disabled")).toBeTruthy();
    expect(screen.getByText(/Popola prima il grafo Knowledge/i)).toBeTruthy();
    expect(screen.queryByRole("link", { name: /Apri mappa/i })).toBeNull();
  });
});
