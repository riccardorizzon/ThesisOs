import { describe, expect, it, afterEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";
import { WritingAiPanel } from "./WritingAiPanel";
import { WRITING_AI_ACTIONS } from "./writingStub";

afterEach(() => {
  cleanup();
});

describe("WritingAiPanel", () => {
  it("renders disabled AI action buttons", () => {
    render(<WritingAiPanel />);

    expect(
      screen.getByRole("complementary", { name: "Azioni AI contestuali" })
    ).toBeTruthy();

    for (const action of WRITING_AI_ACTIONS) {
      const button = screen.getByRole("button", { name: new RegExp(action.label, "i") });
      expect(button).toBeDisabled();
    }
  });

  it("lists contextual action descriptions", () => {
    render(<WritingAiPanel />);

    expect(screen.getByText("Riscrivi")).toBeTruthy();
    expect(screen.getByText(/Riformula il paragrafo selezionato/i)).toBeTruthy();
    expect(screen.getByText("Riassumi")).toBeTruthy();
  });
});
