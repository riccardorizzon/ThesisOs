import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useState } from "react";
import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import {
  MarkdownEditor,
  parseMarkdownSections,
  sectionIdFromHeading,
} from "./MarkdownEditor";

afterEach(() => {
  cleanup();
  vi.useRealTimers();
});

describe("parseMarkdownSections", () => {
  it("extracts heading anchors", () => {
    const content = "# Intro\n\n## §3.2 Metodo\n\nText";
    const sections = parseMarkdownSections(content);
    expect(sections).toHaveLength(2);
    expect(sections[1].id).toBe(sectionIdFromHeading("§3.2 Metodo"));
    expect(sections[1].label).toBe("§3.2 Metodo");
  });
});

describe("MarkdownEditor", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  function ControlledEditor({
    initial = "",
    onSave,
    debounceMs,
  }: {
    initial?: string;
    onSave: (v: string) => Promise<void>;
    debounceMs?: number;
  }) {
    const [value, setValue] = useState(initial);
    return (
      <MarkdownEditor
        value={value}
        onChange={setValue}
        onSave={onSave}
        debounceMs={debounceMs}
      />
    );
  }

  it("debounces autosave by 3 seconds", async () => {
    const onSave = vi.fn().mockResolvedValue(undefined);

    render(<ControlledEditor initial="# Hello" onSave={onSave} debounceMs={3000} />);

    const textarea = screen.getByRole("textbox", { name: "Contenuto capitolo" });
    fireEvent.change(textarea, { target: { value: "# Hello world" } });

    expect(onSave).not.toHaveBeenCalled();

    await act(async () => {
      await vi.advanceTimersByTimeAsync(3000);
    });

    expect(onSave).toHaveBeenCalledWith("# Hello world");
  });

  it("keeps local draft when save fails", async () => {
    const onSave = vi.fn().mockRejectedValue(new Error("network"));

    render(<ControlledEditor onSave={onSave} debounceMs={1000} />);

    const textarea = screen.getByRole("textbox", { name: "Contenuto capitolo" });
    fireEvent.change(textarea, { target: { value: "draft content" } });

    await act(async () => {
      await vi.advanceTimersByTimeAsync(1000);
    });

    expect(onSave).toHaveBeenCalled();
    expect(textarea).toHaveValue("draft content");
    expect(screen.getByTestId("markdown-editor-save-state")).toHaveAttribute(
      "data-save-state",
      "error"
    );
  });

  it("exposes section anchors from headings", () => {
    render(
      <MarkdownEditor
        value={"# Capitolo\n\n## Sezione A"}
        onChange={() => {}}
        onSave={async () => {}}
      />
    );

    const sectionsEl = screen.getByTestId("markdown-editor-sections");
    expect(sectionsEl.querySelector('[data-section-id="capitolo"]')).toBeTruthy();
    expect(sectionsEl.querySelector('[data-section-id="sezione-a"]')).toBeTruthy();
  });
});
