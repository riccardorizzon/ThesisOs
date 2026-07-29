import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { BetaLimitationsPanel } from "./BetaLimitationsPanel";

describe("BetaLimitationsPanel", () => {
  it("renders beta limitation bullets", () => {
    render(<BetaLimitationsPanel />);
    expect(screen.getByTestId("beta-limitations-panel")).toBeTruthy();
    expect(screen.getByText(/Single-user/)).toBeTruthy();
    expect(screen.getByText(/Corpus-bound/)).toBeTruthy();
    expect(screen.getByText(/Tunnel pubblico fragile/)).toBeTruthy();
    expect(screen.getByText(/Originali file/)).toBeTruthy();
  });
});
