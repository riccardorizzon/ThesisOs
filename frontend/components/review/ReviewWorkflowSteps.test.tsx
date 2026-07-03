import { describe, expect, it, afterEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";
import { ReviewWorkflowSteps } from "./ReviewWorkflowSteps";

afterEach(() => {
  cleanup();
});

describe("ReviewWorkflowSteps", () => {
  it("renders all workflow steps", () => {
    render(<ReviewWorkflowSteps current="select" />);

    expect(screen.getByRole("navigation", { name: "Passi revisione" })).toBeTruthy();
    expect(screen.getByText("Seleziona")).toBeTruthy();
    expect(screen.getByText("Confronta")).toBeTruthy();
    expect(screen.getByText("Accetta")).toBeTruthy();
  });

  it("marks the current step as active", () => {
    render(<ReviewWorkflowSteps current="compare" />);

    const active = screen.getByRole("navigation", { name: "Passi revisione" })
      .querySelector("[aria-current='step']");
    expect(active?.textContent).toContain("Confronta");
  });

  it("marks prior steps as complete", () => {
    render(<ReviewWorkflowSteps current="accept" />);

    const nav = screen.getByRole("navigation", { name: "Passi revisione" });
    expect(nav.textContent).toContain("✓");
    expect(nav.querySelectorAll("[aria-current='step']").length).toBe(1);
  });
});
