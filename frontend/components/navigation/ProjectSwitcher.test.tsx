import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { ProjectSwitcher } from "./ProjectSwitcher";
import { DEFAULT_PROJECT_ID } from "@/lib/projectContext";

describe("ProjectSwitcher", () => {
  it("shows current project_id stub", () => {
    render(<ProjectSwitcher />);
    expect(screen.getByText(DEFAULT_PROJECT_ID)).toBeTruthy();
    expect(
      screen.getByRole("button", {
        name: `Progetto attivo: ${DEFAULT_PROJECT_ID}`,
      })
    ).toHaveProperty("disabled", true);
  });
});
