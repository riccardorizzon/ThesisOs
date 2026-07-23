import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

const {
  router,
  replace,
  markWelcomeComplete,
  setWorkspaceMode,
  setActiveProjectId,
} = vi.hoisted(() => ({
  router: { replace: vi.fn() },
  replace: vi.fn(),
  markWelcomeComplete: vi.fn(),
  setWorkspaceMode: vi.fn(),
  setActiveProjectId: vi.fn(),
}));
router.replace = replace;

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
  useRouter: () => router,
}));
vi.mock("@/components/AppShell", () => ({
  AppShell: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="app-shell">{children}</div>
  ),
}));
vi.mock("@/lib/workspacePrefs", () => ({
  getWorkspaceMode: () => "demo",
  hasCompletedWelcome: () => false,
  markWelcomeComplete,
  setWorkspaceMode,
}));
vi.mock("@/lib/projectPrefs", () => ({
  getActiveProjectId: () => "demo-thesis",
  setActiveProjectId,
}));

import { ShellRouter } from "./ShellRouter";

describe("ShellRouter chat-first entry", () => {
  it("opens the personal chat directly and clears persisted demo mode", async () => {
    render(
      <ShellRouter>
        <div data-testid="chat-home" />
      </ShellRouter>,
    );

    expect(screen.getByTestId("chat-home")).toBeInTheDocument();
    await waitFor(() => {
      expect(setActiveProjectId).toHaveBeenCalledWith("thesis-agent");
      expect(setWorkspaceMode).toHaveBeenCalledWith("personal");
      expect(markWelcomeComplete).toHaveBeenCalled();
    });
    expect(replace).not.toHaveBeenCalledWith("/welcome");
  });
});
