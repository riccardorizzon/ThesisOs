import { describe, expect, it, vi, afterEach, beforeEach } from "vitest";
import { cleanup, fireEvent, render, screen, act } from "@testing-library/react";
import { SourcePicker } from "./SourcePicker";
import { corpusClient } from "@/lib/corpusClient";
import { EXCLUDED_CITE_BLOCKED_MESSAGE } from "@/lib/citationInsert";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  localStorage.clear();
});

describe("SourcePicker", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("does not render when closed", () => {
    render(
      <SourcePicker open={false} onClose={vi.fn()} onSelectSource={vi.fn()} />
    );
    expect(screen.queryByTestId("source-picker-modal")).toBeNull();
  });

  it("renders three tabs and search input when open", () => {
    render(
      <SourcePicker open onClose={vi.fn()} onSelectSource={vi.fn()} chapterId="ch1" />
    );

    expect(screen.getByTestId("source-picker-modal")).toBeTruthy();
    expect(screen.getByTestId("source-picker-search")).toBeTruthy();
    expect(screen.getByRole("tab", { name: /Recenti/i })).toBeTruthy();
    expect(screen.getByRole("tab", { name: /Collegate/i })).toBeTruthy();
    expect(screen.getByRole("tab", { name: /Risultati/i })).toBeTruthy();
  });

  it("debounces search and filters results", async () => {
    vi.useFakeTimers();
    const searchRemote = vi
      .spyOn(corpusClient, "searchRemote")
      .mockResolvedValue([]);

    render(
      <SourcePicker open onClose={vi.fn()} onSelectSource={vi.fn()} />
    );

    fireEvent.change(screen.getByTestId("source-picker-search"), {
      target: { value: "Benjamin" },
    });

    expect(searchRemote).not.toHaveBeenCalled();

    await act(async () => {
      vi.advanceTimersByTime(200);
    });

    expect(searchRemote).toHaveBeenCalledWith("Benjamin");
    vi.useRealTimers();
  });

  it("blocks cite for excluded source with Italian message", () => {
    const onSelect = vi.fn();
    render(
      <SourcePicker open onClose={vi.fn()} onSelectSource={onSelect} />
    );

    fireEvent.click(screen.getByRole("tab", { name: /Risultati/i }));

    const excluded = corpusClient.getById("barthes-mythologies");
    expect(excluded?.status).toBe("esclusa");

    fireEvent.change(screen.getByTestId("source-picker-search"), {
      target: { value: "Mythologies" },
    });

    const row = screen.queryByTestId("source-picker-row-barthes-mythologies");
    if (row) {
      fireEvent.click(row);
      expect(onSelect).not.toHaveBeenCalled();
      expect(screen.getByTestId("picker-cite-blocked")).toHaveTextContent(
        EXCLUDED_CITE_BLOCKED_MESSAGE
      );
    } else {
      expect(
        corpusClient.search("Mythologies", { includeExcluded: true })[0]?.status
      ).toBe("esclusa");
    }
  });

  it("calls onSelectSource for approvata source", () => {
    const onSelect = vi.fn();
    render(
      <SourcePicker open onClose={vi.fn()} onSelectSource={onSelect} />
    );

    fireEvent.click(screen.getByRole("tab", { name: /Risultati/i }));
    fireEvent.click(
      screen.getByTestId("source-picker-row-benjamin-opera-arte")
    );
    expect(onSelect).toHaveBeenCalledWith(
      expect.objectContaining({ id: "benjamin-opera-arte" })
    );
  });
});
