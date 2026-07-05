import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { ReviewComparePanel } from "./ReviewComparePanel";

describe("ReviewComparePanel", () => {
  it("shows placeholder when no chapter or proposal selected", () => {
    render(<ReviewComparePanel chapterId={null} proposal={null} />);

    expect(
      screen.getByText(/Seleziona un capitolo con proposte in sospeso/i)
    ).toBeTruthy();
    expect(screen.getByTestId("review-compare-empty")).toBeTruthy();
  });
});
