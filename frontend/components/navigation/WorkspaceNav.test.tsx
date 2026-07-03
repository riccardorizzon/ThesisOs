import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { WorkspaceNav } from "./WorkspaceNav";

describe("WorkspaceNav", () => {
  it("renders nothing without workspace scope", () => {
    const { container } = render(<WorkspaceNav />);
    expect(container.firstChild).toBeNull();
  });

  it("shows workspace id when provided", () => {
    render(<WorkspaceNav workspaceId="ws-thesis" />);
    expect(screen.getByText("ws-thesis")).toBeTruthy();
    expect(screen.getByText(/Workspace:/)).toBeTruthy();
  });
});
