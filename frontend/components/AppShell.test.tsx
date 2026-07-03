import { describe, expect, it, vi, afterEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";
import { AppShell } from "./AppShell";
import { DEFAULT_PROJECT_ID } from "@/lib/projectContext";

vi.mock("next/navigation", () => ({
  usePathname: () => "/writing",
}));

afterEach(() => {
  cleanup();
});

describe("AppShell", () => {
  it("renders primary navigation per ADR-0036", () => {
    render(
      <AppShell>
        <div>Content</div>
      </AppShell>
    );
    const nav = screen.getByRole("navigation", { name: "Primary" });
    expect(nav).toBeTruthy();
    for (const label of ["Home", "Research", "Writing", "Sources", "Knowledge"]) {
      expect(screen.getByRole("link", { name: label })).toBeTruthy();
    }
    expect(screen.getByRole("link", { name: "Settings" })).toBeTruthy();
  });

  it("renders project switcher and breadcrumbs", () => {
    render(
      <AppShell>
        <div>Content</div>
      </AppShell>
    );
    expect(screen.getByText(DEFAULT_PROJECT_ID)).toBeTruthy();
    const breadcrumb = screen.getByRole("navigation", { name: "Breadcrumb" });
    expect(breadcrumb).toBeTruthy();
    expect(
      breadcrumb.querySelector('[aria-current="page"]')?.textContent
    ).toBe("Writing");
  });

  it("renders optional right panel slot", () => {
    render(
      <AppShell rightPanel={<div>AI Panel</div>}>
        <div>Content</div>
      </AppShell>
    );
    expect(screen.getByRole("complementary", { name: "Panel" })).toBeTruthy();
    expect(screen.getByText("AI Panel")).toBeTruthy();
  });

  it("omits right panel when not provided", () => {
    render(
      <AppShell>
        <div>Content</div>
      </AppShell>
    );
    expect(screen.queryByRole("complementary", { name: "Panel" })).toBeNull();
  });
});
