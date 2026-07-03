import { describe, expect, it, vi, afterEach } from "vitest";
import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import { ReviewMode } from "./ReviewMode";

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

afterEach(() => {
  cleanup();
});

describe("ReviewMode", () => {
  it("renders review shell with workflow steps", () => {
    render(<ReviewMode />);

    expect(screen.getByRole("heading", { name: "Revisione" })).toBeTruthy();
    expect(screen.getByRole("navigation", { name: "Passi revisione" })).toBeTruthy();
    expect(screen.getByText("Seleziona")).toBeTruthy();
    expect(screen.getByText("Confronta")).toBeTruthy();
    expect(screen.getByText("Accetta")).toBeTruthy();
  });

  it("links to /ai as distinct power mode", () => {
    render(<ReviewMode />);

    expect(screen.getByRole("link", { name: "/ai" })).toHaveAttribute("href", "/ai");
  });

  it("advances workflow from select to compare to accept", () => {
    render(<ReviewMode />);

    fireEvent.click(screen.getByText("Capitolo 1 — Introduzione"));
    fireEvent.click(screen.getByRole("button", { name: "Confronta revisione" }));

    expect(screen.getByText("Versione corrente")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Accetta revisione" })).not.toBeDisabled();

    fireEvent.click(screen.getByRole("button", { name: "Accetta revisione" }));
    expect(screen.getByRole("status")).toHaveTextContent(/Revisione accettata/i);
  });

  it("lists stub chapters in selector", () => {
    render(<ReviewMode />);

    expect(screen.getByText("Capitolo 1 — Introduzione")).toBeTruthy();
    expect(screen.getByText("Capitolo 2 — Metodo")).toBeTruthy();
    expect(screen.getByText("Capitolo 3 — Analisi")).toBeTruthy();
  });
});
