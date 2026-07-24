import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { DemoWorkspaceBanner } from "@/components/workspace/DemoWorkspaceBanner";
import { chapterClient } from "@/lib/chapterClient";
import { setActiveProjectId } from "@/lib/projectPrefs";

const push = vi.fn();
const refresh = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push, refresh }),
}));

vi.mock("@/lib/chapterClient", () => ({
  chapterClient: { copyDemoStructure: vi.fn() },
}));

vi.mock("@/lib/projectsClient", () => ({
  createProject: vi.fn(),
}));

vi.mock("@/lib/projectPrefs", () => ({
  getLastPersonalProjectId: () => "thesis-002",
  saveProjectPrefs: vi.fn(),
  setActiveProjectId: vi.fn(),
}));

vi.mock("@/lib/workspacePrefs", () => ({
  setWorkspaceMode: vi.fn(),
}));

beforeEach(() => {
  vi.mocked(chapterClient.copyDemoStructure).mockResolvedValue({
    created: [],
    skipped_titles: [],
  });
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("DemoWorkspaceBanner", () => {
  it("copies the demo structure into the last personal thesis, never demo-thesis", async () => {
    render(<DemoWorkspaceBanner />);

    fireEvent.click(screen.getByTestId("demo-copy-structure"));
    fireEvent.click(screen.getByTestId("copy-structure-confirm"));

    await waitFor(() => {
      expect(chapterClient.copyDemoStructure).toHaveBeenCalledWith("thesis-002");
    });
    expect(setActiveProjectId).toHaveBeenCalledWith("thesis-002");
    expect(push).toHaveBeenCalledWith("/writing");
  });
});
