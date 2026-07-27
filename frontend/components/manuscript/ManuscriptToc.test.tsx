import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ManuscriptToc } from "./ManuscriptToc";
import type { ManuscriptOutlinePart } from "@/lib/manuscriptToc";

afterEach(() => cleanup());

const outline: ManuscriptOutlinePart[] = [
  {
    number: "1",
    title: "Capitolo 1",
    chapterId: null,
    status: null,
    word_count: 0,
    sections: [
      {
        id: "s11",
        number: "1.1",
        label: "Intro",
        status: "review",
        word_count: 10,
        order_index: 0,
      },
    ],
  },
  {
    number: "3",
    title: "Progettazione metodologica",
    chapterId: "c3",
    status: "review",
    word_count: 100,
    sections: [
      {
        id: "s36",
        number: "3.6",
        label: "Sintesi: il capo come costruzione di senso",
        status: "draft",
        word_count: 177,
        order_index: 36,
      },
    ],
  },
];

describe("ManuscriptToc", () => {
  it("shows hierarchical index with section numbers and labels", () => {
    render(
      <ManuscriptToc
        outline={outline}
        activeChapterId="s36"
        onSelectChapter={vi.fn()}
      />
    );
    expect(screen.getByText(/Capitoli e sottocapitoli/i)).toBeTruthy();
    expect(screen.getByText("3.6")).toBeTruthy();
    expect(screen.getByText("Sintesi: il capo come costruzione di senso")).toBeTruthy();
    expect(screen.getByText("1.1")).toBeTruthy();
    expect(screen.getByText("Intro")).toBeTruthy();
    expect(screen.getByText("Progettazione metodologica")).toBeTruthy();
  });

  it("selects chapter headers and sections", () => {
    const onSelectChapter = vi.fn();
    render(
      <ManuscriptToc
        outline={outline}
        activeChapterId="s36"
        onSelectChapter={onSelectChapter}
      />
    );
    fireEvent.click(screen.getByRole("button", { name: /Progettazione metodologica/i }));
    expect(onSelectChapter).toHaveBeenCalledWith("c3");
    fireEvent.click(
      screen.getByRole("button", { name: /3\.6 Sintesi: il capo come costruzione di senso/i })
    );
    expect(onSelectChapter).toHaveBeenCalledWith("s36");
  });
});
