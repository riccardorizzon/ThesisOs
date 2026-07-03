import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { ReviewComparePanel } from "./ReviewComparePanel";
import type { ReviewChapter } from "./reviewStub";

const TEST_CHAPTER: ReviewChapter = {
  id: "cap-1",
  title: "Capitolo 1 — Introduzione",
  status: "revisione",
  pendingChanges: 1,
};

describe("ReviewComparePanel", () => {
  it("shows placeholder when no chapter selected", () => {
    render(<ReviewComparePanel chapter={null} />);

    expect(
      screen.getByText(/Seleziona un capitolo per visualizzare il confronto/i)
    ).toBeTruthy();
  });

  it("shows side-by-side diff stub when chapter selected", () => {
    render(<ReviewComparePanel chapter={TEST_CHAPTER} />);

    expect(screen.getByText("Versione corrente")).toBeTruthy();
    expect(screen.getByText("Revisione proposta")).toBeTruthy();
    expect(screen.getByText(/Capitolo 1 — Introduzione/)).toBeTruthy();
  });
});
