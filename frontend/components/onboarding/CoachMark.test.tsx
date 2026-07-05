import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import {
  CoachMark,
  CoachMarkProvider,
  ONBOARDING_STORAGE_KEY,
  PX2_COACH_STEPS,
} from "./CoachMark";

beforeEach(() => {
  localStorage.clear();
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: false,
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    })),
  });
});

afterEach(() => {
  cleanup();
  localStorage.clear();
});

describe("CoachMark", () => {
  it("renders step content and skip control", () => {
    document.body.innerHTML =
      '<a data-testid="continua-link" href="/writing">Continua</a>';

    render(
      <CoachMark
        step={PX2_COACH_STEPS[0]}
        onNext={vi.fn()}
        onSkip={vi.fn()}
        stepIndex={0}
        totalSteps={3}
      />
    );

    expect(screen.getByTestId("coach-mark-step-1")).toBeTruthy();
    expect(screen.getByText("Riprendi da dove hai lasciato")).toBeTruthy();
    expect(screen.getByTestId("coach-mark-skip")).toBeTruthy();
  });
});

describe("CoachMarkProvider", () => {
  it("dismisses forever when skip is clicked", () => {
    document.body.innerHTML =
      '<a data-testid="continua-link" href="/writing">Continua</a>';

    render(<CoachMarkProvider pathname="/" />);

    fireEvent.click(screen.getByTestId("coach-mark-skip"));

    const stored = JSON.parse(
      localStorage.getItem(ONBOARDING_STORAGE_KEY) ?? "{}"
    ) as { dismissed: boolean };
    expect(stored.dismissed).toBe(true);
    expect(screen.queryByTestId("coach-mark-step-1")).toBeNull();
  });

  it("limits onboarding to three steps", () => {
    expect(PX2_COACH_STEPS).toHaveLength(3);
  });
});
