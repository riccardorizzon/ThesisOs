import { describe, expect, it, vi, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";
import { ReviewDocumentSelector } from "./ReviewDocumentSelector";
import type { ReviewChapter } from "./reviewStub";

afterEach(() => {
  cleanup();
});

const TEST_CHAPTERS: ReviewChapter[] = [
  {
    id: "cap-1",
    title: "Capitolo 1 — Introduzione",
    status: "revisione",
    pendingChanges: 2,
  },
  {
    id: "cap-2",
    title: "Capitolo 2 — Metodo",
    status: "bozza",
    pendingChanges: 0,
  },
];

describe("ReviewDocumentSelector", () => {
  it("renders chapter options", () => {
    render(
      <ReviewDocumentSelector
        chapters={TEST_CHAPTERS}
        selectedId={null}
        onSelect={vi.fn()}
      />
    );

    expect(screen.getByText("Capitolo 1 — Introduzione")).toBeTruthy();
    expect(screen.getByText("Capitolo 2 — Metodo")).toBeTruthy();
    expect(screen.getByText(/2 modifiche in sospeso/)).toBeTruthy();
  });

  it("calls onSelect when a chapter is clicked", () => {
    const onSelect = vi.fn();
    render(
      <ReviewDocumentSelector
        chapters={TEST_CHAPTERS}
        selectedId={null}
        onSelect={onSelect}
      />
    );

    fireEvent.click(screen.getByText("Capitolo 1 — Introduzione"));
    expect(onSelect).toHaveBeenCalledWith("cap-1");
  });
});
