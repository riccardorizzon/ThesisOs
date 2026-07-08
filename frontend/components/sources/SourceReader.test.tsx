import { describe, expect, it, vi, afterEach } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { SourceReader } from "./SourceReader";
import {
  FIXTURE_APPROVED_CORPUS_SOURCE,
  FIXTURE_EXCLUDED_CORPUS_SOURCE,
} from "@/lib/fixtures/corpusFixture";
import {
  dispatchInsertCitation,
  EXCLUDED_CITE_BLOCKED_MESSAGE,
  INSERT_CITATION_EVENT,
} from "@/lib/citationInsert";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

const approvedSource = FIXTURE_APPROVED_CORPUS_SOURCE;
const excludedSource = FIXTURE_EXCLUDED_CORPUS_SOURCE;

describe("SourceReader", () => {
  it("renders full variant with metadata and body", () => {
    render(<SourceReader source={approvedSource} variant="full" />);

    expect(screen.getByTestId("source-reader-full")).toBeTruthy();
    expect(screen.getByRole("heading", { name: approvedSource.title })).toBeTruthy();
    expect(screen.getByText("Walter Benjamin")).toBeTruthy();
    expect(screen.getByTestId("source-reader-body")).toBeTruthy();
    expect(screen.getByTestId("insert-citation-btn")).toHaveAttribute(
      "aria-disabled",
      "false"
    );
  });

  it("renders peek variant with dismiss control", () => {
    const onDismiss = vi.fn();
    render(
      <SourceReader
        source={approvedSource}
        variant="peek"
        onDismiss={onDismiss}
      />
    );

    expect(screen.getByTestId("source-reader-peek")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Chiudi" }));
    expect(onDismiss).toHaveBeenCalled();
  });

  it("blocks citation for excluded sources", async () => {
    render(<SourceReader source={excludedSource} variant="full" />);

    fireEvent.click(screen.getByTestId("insert-citation-btn"));
    await waitFor(() => {
      expect(screen.getByText(EXCLUDED_CITE_BLOCKED_MESSAGE)).toBeTruthy();
    });
  });

  it("dispatches insert citation event on approved source", () => {
    const listener = vi.fn();
    window.addEventListener(INSERT_CITATION_EVENT, listener);

    render(<SourceReader source={approvedSource} variant="full" />);
    fireEvent.click(screen.getByTestId("insert-citation-btn"));

    expect(listener).toHaveBeenCalled();
    window.removeEventListener(INSERT_CITATION_EVENT, listener);
  });

  it("calls onCite when provided", () => {
    const onCite = vi.fn();
    render(
      <SourceReader source={approvedSource} variant="full" onCite={onCite} />
    );

    fireEvent.click(screen.getByTestId("insert-citation-btn"));
    expect(onCite).toHaveBeenCalledWith(approvedSource, undefined);
  });

  it("supports programmatic citation dispatch", () => {
    render(<SourceReader source={approvedSource} variant="full" />);
    dispatchInsertCitation({
      marker: "[@Benjamin1936]",
      sourceId: approvedSource.id,
      quote: "Test quote",
    });
    expect(screen.getByTestId("source-reader-full")).toBeTruthy();
  });
});
