import { describe, expect, it, afterEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";
import { WritingEditorShell } from "./WritingEditorShell";

afterEach(() => {
  cleanup();
});

describe("WritingEditorShell", () => {
  it("prompts to select a chapter when no chapterId", () => {
    render(<WritingEditorShell />);

    expect(screen.getByRole("region", { name: "Editor Markdown" })).toBeTruthy();
    expect(
      screen.getByText(/Scegli un capitolo dall'outline/i)
    ).toBeTruthy();
  });

  it("renders markdown placeholder for selected chapter", () => {
    render(<WritingEditorShell chapterId="2" />);

    expect(screen.getByText("Cap. 2 — Quadro teorico")).toBeTruthy();
    expect(screen.getByTestId("writing-editor-placeholder")).toBeTruthy();
    expect(screen.getByText(/Contenuto capitolo 2/i)).toBeTruthy();
  });
});
