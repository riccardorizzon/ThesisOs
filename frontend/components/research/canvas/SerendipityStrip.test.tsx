import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";

import { SerendipityStrip } from "./SerendipityStrip";
import type { SerendipitySuggestion } from "@/lib/canvasSerendipity";

const SUGGESTIONS: SerendipitySuggestion[] = [
  {
    id: "bridge:aura:mito:stigmata",
    type: "bridge",
    title: "Ponte concetti",
    subtitle: "Aura ↔ Mito via STIGMATA",
    actionLabel: "Mostra",
    targetSlugs: ["aura", "mito", "stigmata"],
    targetEdgeKeys: ["aura-stigmata-contradicts"],
    rank: 1,
  },
];

describe("SerendipityStrip", () => {
  it("renders suggestion cards and handles activation", () => {
    const onActivate = vi.fn();
    render(<SerendipityStrip suggestions={SUGGESTIONS} onSuggestionActivate={onActivate} />);

    expect(screen.getByTestId("canvas-serendipity-strip")).toBeTruthy();
    expect(screen.getByTestId("serendipity-card-bridge")).toBeTruthy();
    fireEvent.click(screen.getByTestId("serendipity-card-bridge"));
    expect(onActivate).toHaveBeenCalledWith(SUGGESTIONS[0]);
  });

  it("renders nothing when suggestions are empty", () => {
    const { container } = render(
      <SerendipityStrip suggestions={[]} onSuggestionActivate={vi.fn()} />
    );
    expect(container.firstChild).toBeNull();
  });
});
