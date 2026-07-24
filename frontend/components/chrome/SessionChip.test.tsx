import { act, cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { SessionChip } from "@/components/chrome/SessionChip";

beforeEach(() => {
  localStorage.clear();
  vi.useFakeTimers();
  vi.setSystemTime(new Date("2026-07-04T12:00:00Z"));
});

afterEach(() => {
  cleanup();
  vi.useRealTimers();
  localStorage.clear();
});

describe("SessionChip", () => {
  it("starts below one minute and advances on the minute boundary", () => {
    render(<SessionChip />);
    expect(screen.getByTestId("session-chip")).toHaveTextContent("Sessione·<1m");

    act(() => {
      vi.advanceTimersByTime(60_000);
    });

    expect(screen.getByTestId("session-chip")).toHaveTextContent("Sessione·1m");
  });
});
