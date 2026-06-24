import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MemoryList } from "@/components/MemoryList";
import type { Memory } from "@/lib/memoryClient";

const sample: Memory[] = [
  {
    id: "a",
    kind: "concept",
    title: "Thesis scope",
    content: "notes",
    metadata: {},
    key: null,
    pinned: false,
    source: "user",
    version: 2,
    created_at: "2026-06-24T10:00:00Z",
    updated_at: "2026-06-24T11:00:00Z",
  },
];

describe("MemoryList", () => {
  it("renders list rows with kind badge and version", () => {
    render(<MemoryList items={sample} />);
    expect(screen.getByTestId("memory-list")).toBeInTheDocument();
    expect(screen.getByText("Thesis scope")).toBeInTheDocument();
    expect(screen.getByTestId("kind-badge-concept")).toBeInTheDocument();
    expect(screen.getByText("v2")).toBeInTheDocument();
  });

  it("shows empty state", () => {
    render(<MemoryList items={[]} />);
    expect(screen.getByText("No memories found.")).toBeInTheDocument();
  });
});
