import { describe, expect, it, vi, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";
import { ReviewActionBar } from "./ReviewActionBar";

afterEach(() => {
  cleanup();
});

describe("ReviewActionBar", () => {
  it("disables actions when not enabled", () => {
    render(
      <ReviewActionBar
        enabled={false}
        onAccept={vi.fn()}
        onReject={vi.fn()}
      />
    );

    expect(screen.getByRole("button", { name: "Accetta revisione" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Rifiuta" })).toBeDisabled();
    expect(
      screen.getByText(/Completa il confronto per abilitare/i)
    ).toBeTruthy();
  });

  it("invokes accept and reject handlers when enabled", () => {
    const onAccept = vi.fn();
    const onReject = vi.fn();
    render(
      <ReviewActionBar
        enabled={true}
        onAccept={onAccept}
        onReject={onReject}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "Accetta revisione" }));
    fireEvent.click(screen.getByRole("button", { name: "Rifiuta" }));
    expect(onAccept).toHaveBeenCalledTimes(1);
    expect(onReject).toHaveBeenCalledTimes(1);
  });

  it("shows feedback message when provided", () => {
    render(
      <ReviewActionBar
        enabled={true}
        onAccept={vi.fn()}
        onReject={vi.fn()}
        feedback="Revisione accettata (stub)."
      />
    );

    expect(screen.getByRole("status")).toHaveTextContent(
      "Revisione accettata (stub)."
    );
  });
});
