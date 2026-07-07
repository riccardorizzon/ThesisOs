import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { ProjectSwitcher } from "./ProjectSwitcher";
import { DEFAULT_PROJECT_ID } from "@/lib/projectContext";

vi.mock("@/lib/projectsClient", () => ({
  listProjects: vi.fn().mockResolvedValue([
    {
      id: "thesis-agent",
      display_name: "Tesi di laurea",
      created_at: "2026-07-01T00:00:00Z",
    },
  ]),
  createProject: vi.fn(),
}));

describe("ProjectSwitcher", () => {
  it("shows active project display name", async () => {
    render(<ProjectSwitcher />);
    await waitFor(() => {
      expect(screen.getByText("Tesi di laurea")).toBeTruthy();
    });
    expect(screen.getByRole("button", { name: /Tesi di laurea/ })).toBeTruthy();
  });
});
