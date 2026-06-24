import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MemoryVersionList } from "@/components/MemoryVersionList";

describe("MemoryVersionList", () => {
  it("renders version history read-only", () => {
    render(
      <MemoryVersionList
        versions={[
          {
            memory_id: "m1",
            version: 1,
            title: "T",
            content: "v1 body",
            metadata: {},
            source: "user",
            changed_at: "2026-06-24T10:00:00Z",
          },
        ]}
      />,
    );
    expect(screen.getByTestId("memory-version-list")).toBeInTheDocument();
    expect(screen.getByText("Version 1")).toBeInTheDocument();
    expect(screen.getByText(/Restore is not available/)).toBeInTheDocument();
  });
});
