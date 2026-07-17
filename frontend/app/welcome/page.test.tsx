import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import WelcomePage from "@/app/welcome/page";
import { createProject } from "@/lib/projectsClient";
import { saveProjectPrefs, setActiveProjectId } from "@/lib/projectPrefs";
import { markWelcomeComplete, setWorkspaceMode } from "@/lib/workspacePrefs";

const push = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

vi.mock("@/lib/workspacePrefs", () => ({
  setWorkspaceMode: vi.fn(),
  markWelcomeComplete: vi.fn(),
}));

vi.mock("@/lib/projectPrefs", () => ({
  setActiveProjectId: vi.fn(),
  saveProjectPrefs: vi.fn(),
}));

vi.mock("@/lib/projectsClient", () => ({
  createProject: vi.fn().mockResolvedValue({
    id: "nuova-tesi-abc123",
    display_name: "Nuova tesi 2026-07-17",
    created_at: "2026-07-17T00:00:00Z",
    kind: "owned",
  }),
}));

afterEach(() => {
  cleanup();
});

describe("WelcomePage", () => {
  it("creates an isolated project for Nuova tesi", async () => {
    push.mockClear();
    render(<WelcomePage />);
    fireEvent.click(screen.getByTestId("welcome-new-thesis"));
    await waitFor(() => {
      expect(createProject).toHaveBeenCalled();
      expect(setActiveProjectId).toHaveBeenCalledWith("nuova-tesi-abc123");
      expect(setWorkspaceMode).toHaveBeenCalledWith("personal");
      expect(markWelcomeComplete).toHaveBeenCalled();
      expect(saveProjectPrefs).toHaveBeenCalled();
      expect(push).toHaveBeenCalledWith("/");
    });
  });

  it("forces demo-thesis for Esplora demo", () => {
    push.mockClear();
    render(<WelcomePage />);
    fireEvent.click(screen.getByTestId("welcome-explore-demo"));
    expect(setActiveProjectId).toHaveBeenCalledWith("demo-thesis");
    expect(setWorkspaceMode).toHaveBeenCalledWith("demo");
    expect(markWelcomeComplete).toHaveBeenCalled();
    expect(push).toHaveBeenCalledWith("/");
  });
});
