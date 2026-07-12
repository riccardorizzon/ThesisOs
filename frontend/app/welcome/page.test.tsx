import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import WelcomePage from "@/app/welcome/page";

const push = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

vi.mock("@/lib/workspacePrefs", () => ({
  setWorkspaceMode: vi.fn(),
  markWelcomeComplete: vi.fn(),
}));

describe("WelcomePage", () => {
  it("routes new thesis to personal writing workspace", () => {
    push.mockClear();
    render(<WelcomePage />);

    fireEvent.click(screen.getByTestId("welcome-new-thesis"));
    expect(push).toHaveBeenCalledWith("/writing");
  });
});
