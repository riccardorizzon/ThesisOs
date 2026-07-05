import { describe, expect, it, vi, afterEach } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { SourceReader } from "./SourceReader";
import { corpusClient } from "@/lib/corpusClient";
import {
  dispatchInsertCitation,
  EXCLUDED_CITE_BLOCKED_MESSAGE,
  INSERT_CITATION_EVENT,
} from "@/lib/citationInsert";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

const approvedSource = corpusClient.getById("benjamin-opera-arte")!;
const excludedSource = corpusClient.getById("barthes-mythologies")!;

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
    fireEvent.click(screen.getByTestId("peek-dismiss-btn"));
    expect(onDismiss).toHaveBeenCalled();
  });

  it("copies quote via copy button", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, {
      clipboard: { writeText },
    });

    render(<SourceReader source={approvedSource} variant="full" />);
    fireEvent.click(screen.getByTestId("copy-quote-btn"));

    await waitFor(() => {
      expect(writeText).toHaveBeenCalled();
    });
    await waitFor(() => {
      expect(screen.getByText("Copiato")).toBeTruthy();
    });
  });

  it("blocks citation for excluded source", () => {
    render(<SourceReader source={excludedSource} variant="full" />);

    expect(screen.getByTestId("source-excluded-ban")).toBeTruthy();
    expect(screen.getByTestId("source-exclusion-reason")).toBeTruthy();
    expect(screen.getByTestId("insert-citation-btn")).toHaveAttribute(
      "aria-disabled",
      "true"
    );

    fireEvent.click(screen.getByTestId("insert-citation-btn"));
    expect(screen.getByTestId("cite-blocked-message")).toHaveTextContent(
      EXCLUDED_CITE_BLOCKED_MESSAGE
    );
  });

  it("dispatches insert-citation event on cite", () => {
    const handler = vi.fn();
    window.addEventListener(INSERT_CITATION_EVENT, handler);

    render(<SourceReader source={approvedSource} variant="full" />);
    fireEvent.click(screen.getByTestId("insert-citation-btn"));

    expect(handler).toHaveBeenCalled();
    const event = handler.mock.calls[0][0] as CustomEvent;
    expect(event.detail.sourceId).toBe("benjamin-opera-arte");
    expect(event.detail.marker).toMatch(/\[@Benjamin1936\]/);

    window.removeEventListener(INSERT_CITATION_EVENT, handler);
  });
});

describe("dispatchInsertCitation", () => {
  it("is re-exported from citationInsert module", () => {
    const handler = vi.fn();
    window.addEventListener(INSERT_CITATION_EVENT, handler);
    dispatchInsertCitation({ marker: "[@Test2020]", sourceId: "test" });
    expect(handler).toHaveBeenCalled();
    window.removeEventListener(INSERT_CITATION_EVENT, handler);
  });
});
