import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { ProgressRing } from "./ProgressRing";

describe("ProgressRing", () => {
  it("clamps value to 0–100", () => {
    render(<ProgressRing value={150} label="Progress" />);
    expect(screen.getByText("100%")).toBeTruthy();
  });

  it("renders label and sublabel", () => {
    render(
      <ProgressRing
        value={42}
        label="Avanzamento"
        sublabel="Capitoli in revisione"
      />
    );
    expect(screen.getByText("Avanzamento")).toBeTruthy();
    expect(screen.getByText("Capitoli in revisione")).toBeTruthy();
    expect(screen.getByText("42%")).toBeTruthy();
  });

  it("exposes accessible progress text", () => {
    render(<ProgressRing value={33} />);
    expect(screen.getByText("33 percent complete")).toBeTruthy();
  });
});
