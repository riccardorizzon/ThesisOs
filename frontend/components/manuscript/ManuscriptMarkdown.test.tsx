import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { sectionIdFromHeading } from "@/components/writing/MarkdownEditor";
import { ManuscriptMarkdown } from "./ManuscriptMarkdown";

afterEach(() => cleanup());

describe("ManuscriptMarkdown", () => {
  it("renders headings with stable section ids", () => {
    render(<ManuscriptMarkdown content={"# Intro\n\n## Method\n\nHello world."} />);
    const h1 = screen.getByRole("heading", { level: 1, name: "Intro" });
    expect(h1.id).toBe(sectionIdFromHeading("Intro"));
    expect(screen.getByRole("heading", { level: 2, name: "Method" }).id).toBe(
      sectionIdFromHeading("Method")
    );
    expect(screen.getByText("Hello world.")).toBeTruthy();
  });

  it("renders empty content without crashing", () => {
    const { container } = render(<ManuscriptMarkdown content="" />);
    expect(container.querySelector("[data-testid='manuscript-markdown']")).toBeTruthy();
  });

  it("renders unordered lists and fenced code blocks", () => {
    render(
      <ManuscriptMarkdown
        content={"# List\n\n- one\n- two\n\n```\ncode line\n```"}
      />
    );
    expect(screen.getByRole("list")).toBeTruthy();
    expect(screen.getByText("one")).toBeTruthy();
    expect(screen.getByText("two")).toBeTruthy();
    expect(screen.getByText("code line")).toBeTruthy();
  });
});
