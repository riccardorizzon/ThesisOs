import { describe, expect, it, vi, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";
import { ResearchLensRail } from "./ResearchLensRail";

afterEach(() => {
  cleanup();
});

describe("ResearchLensRail", () => {
  it("renders all lenses and marks active lens", () => {
    const onLensChange = vi.fn();
    render(<ResearchLensRail activeLensId="L-all" onLensChange={onLensChange} />);
    expect(screen.getByTestId("canvas-lens-L-all")).toBeTruthy();
    expect(screen.getByTestId("canvas-lens-L-controversy")).toBeTruthy();
    fireEvent.click(screen.getByTestId("canvas-lens-L-gap"));
    expect(onLensChange).toHaveBeenCalledWith("L-gap");
  });
});
