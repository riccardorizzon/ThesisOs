import { describe, expect, it, afterEach } from "vitest";
import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import { WritingWorkspace } from "./WritingWorkspace";

afterEach(() => {
  cleanup();
});

describe("WritingWorkspace", () => {
  it("renders three-panel shell with outline, editor, and AI panel", () => {
    render(<WritingWorkspace chapterId="1" />);

    expect(screen.getByTestId("writing-workspace")).toBeTruthy();
    expect(screen.getByRole("navigation", { name: "Outline capitoli" })).toBeTruthy();
    expect(screen.getByRole("region", { name: "Editor Markdown" })).toBeTruthy();
    expect(
      screen.getByRole("complementary", { name: "Azioni AI contestuali" })
    ).toBeTruthy();
  });

  it("highlights active chapter in outline", () => {
    render(<WritingWorkspace chapterId="4" />);

    expect(
      screen.getByRole("link", { name: /Cap\. 4 — Analisi/i })
    ).toHaveAttribute("aria-current", "page");
  });

  it("toggles outline panel on small screens", () => {
    render(<WritingWorkspace chapterId="2" />);

    const outlineToggle = screen.getByRole("button", { name: "Outline" });
    const outlinePanel = document.getElementById("writing-outline-panel");

    expect(outlinePanel?.className).toMatch(/hidden/);

    fireEvent.click(outlineToggle);
    expect(outlinePanel?.className).toMatch(/block/);
    expect(outlineToggle).toHaveAttribute("aria-pressed", "true");
  });

  it("toggles AI panel on small screens", () => {
    render(<WritingWorkspace />);

    const aiToggle = screen.getByRole("button", { name: "Azioni AI" });
    const aiPanel = document.getElementById("writing-ai-panel");

    expect(aiPanel?.className).toMatch(/hidden/);

    fireEvent.click(aiToggle);
    expect(aiPanel?.className).toMatch(/block/);
    expect(aiToggle).toHaveAttribute("aria-pressed", "true");
  });
});
