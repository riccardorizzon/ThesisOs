import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { MemoryKindBadge } from "@/components/MemoryKindBadge";

describe("MemoryKindBadge", () => {
  afterEach(() => cleanup());

  it("renders kind label with test id", () => {
    render(<MemoryKindBadge kind="editable" />);
    expect(screen.getByTestId("kind-badge-editable")).toHaveTextContent("editable");
  });

  it("renders all operational and knowledge kinds", () => {
    const kinds = [
      "user",
      "thesis",
      "editable",
      "decision",
      "concept",
      "citation",
      "note",
    ] as const;
    for (const kind of kinds) {
      render(<MemoryKindBadge kind={kind} />);
      expect(screen.getByTestId(`kind-badge-${kind}`)).toBeInTheDocument();
      cleanup();
    }
  });
});
