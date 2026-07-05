import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, render } from "@testing-library/react";
import { useKeyboardShortcuts } from "./useKeyboardShortcuts";

const push = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

function ShortcutHarness() {
  useKeyboardShortcuts();
  return <div data-testid="harness" />;
}

afterEach(() => {
  cleanup();
  push.mockReset();
});

describe("useKeyboardShortcuts", () => {
  beforeEach(() => {
    push.mockReset();
  });

  it("navigates to Writing on G then W chord", () => {
    render(<ShortcutHarness />);

    window.dispatchEvent(new KeyboardEvent("keydown", { key: "g", bubbles: true }));
    window.dispatchEvent(new KeyboardEvent("keydown", { key: "w", bubbles: true }));

    expect(push).toHaveBeenCalledWith("/writing");
  });

  it("dispatches open palette event on meta+k", () => {
    const handler = vi.fn();
    window.addEventListener("thesisos:open-command-palette", handler);
    render(<ShortcutHarness />);

    const event = new KeyboardEvent("keydown", {
      key: "k",
      metaKey: true,
      bubbles: true,
      cancelable: true,
    });
    window.dispatchEvent(event);

    expect(handler).toHaveBeenCalled();
    window.removeEventListener("thesisos:open-command-palette", handler);
  });
});
