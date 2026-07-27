import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ManuscriptToc } from "./ManuscriptToc";
import type { ManuscriptTocChapter } from "@/lib/manuscriptToc";

afterEach(() => cleanup());

const chapters: ManuscriptTocChapter[] = [
  {
    id: "c1",
    title: "Capitolo 1",
    status: "draft",
    word_count: 100,
    order_index: 0,
    sections: [
      { id: "intro", label: "Intro", level: 1 },
      { id: "method", label: "Method", level: 2 },
    ],
  },
  {
    id: "c2",
    title: "Capitolo 2",
    status: "approved",
    word_count: 50,
    order_index: 1,
    sections: [],
  },
];

describe("ManuscriptToc", () => {
  it("shows summary, statuses, words, and sections", () => {
    render(
      <ManuscriptToc
        chapters={chapters}
        activeChapterId="c1"
        onSelectChapter={vi.fn()}
        onSelectSection={vi.fn()}
      />
    );
    expect(screen.getByTestId("manuscript-toc")).toBeTruthy();
    expect(screen.getByText(/2 capitoli/i)).toBeTruthy();
    expect(screen.getByText(/150/)).toBeTruthy();
    expect(screen.getByTestId("status-badge-draft")).toBeTruthy();
    expect(screen.getByText("Intro")).toBeTruthy();
    expect(screen.getByText("Method")).toBeTruthy();
  });

  it("notifies chapter and section selection", () => {
    const onSelectChapter = vi.fn();
    const onSelectSection = vi.fn();
    render(
      <ManuscriptToc
        chapters={chapters}
        activeChapterId="c1"
        onSelectChapter={onSelectChapter}
        onSelectSection={onSelectSection}
      />
    );
    fireEvent.click(screen.getByRole("button", { name: /Capitolo 2/i }));
    expect(onSelectChapter).toHaveBeenCalledWith("c2");
    fireEvent.click(screen.getByRole("button", { name: "Method" }));
    expect(onSelectSection).toHaveBeenCalledWith("c1", "method");
  });
});
