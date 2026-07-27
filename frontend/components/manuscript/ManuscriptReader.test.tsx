import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { Chapter } from "@/lib/chapterClient";
import { ManuscriptReader } from "./ManuscriptReader";

afterEach(() => cleanup());

const chapter: Chapter = {
  id: "c2",
  parent_id: null,
  order_index: 1,
  title: "Capitolo 2",
  status: "draft",
  content_md: "# Hello\n\nBody.",
  summary: null,
  word_count: 2,
  version: 1,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

describe("ManuscriptReader", () => {
  it("renders title, markdown, and navigates prev/next", () => {
    const onNavigate = vi.fn();
    render(
      <ManuscriptReader
        chapter={chapter}
        prevId="c1"
        nextId="c3"
        onNavigate={onNavigate}
      />
    );
    expect(screen.getByTestId("manuscript-reader")).toBeTruthy();
    expect(screen.getByRole("heading", { name: "Capitolo 2" })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Precedente" }));
    expect(onNavigate).toHaveBeenCalledWith("c1");
    fireEvent.click(screen.getByRole("button", { name: "Successivo" }));
    expect(onNavigate).toHaveBeenCalledWith("c3");
    expect(screen.getByTestId("manuscript-edit").getAttribute("href")).toBe("/writing/c2");
  });

  it("shows empty thesis CTA", () => {
    render(
      <ManuscriptReader
        chapter={null}
        prevId={null}
        nextId={null}
        emptyThesis
        onNavigate={vi.fn()}
      />
    );
    expect(screen.getByRole("link", { name: /Writing/i })).toBeTruthy();
  });

  it("shows empty chapter message when content missing", () => {
    render(
      <ManuscriptReader
        chapter={{ ...chapter, content_md: "" }}
        prevId={null}
        nextId={null}
        onNavigate={vi.fn()}
      />
    );
    expect(screen.getByText(/Ancora vuoto/i)).toBeTruthy();
  });
});
