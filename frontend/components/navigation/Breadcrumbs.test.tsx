import { describe, expect, it, vi, afterEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";
import { Breadcrumbs } from "./Breadcrumbs";

vi.mock("next/navigation", () => ({
  usePathname: vi.fn(() => "/writing/ch-1"),
}));

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("Breadcrumbs", () => {
  it("renders module and nested segments", async () => {
    const { usePathname } = await import("next/navigation");
    vi.mocked(usePathname).mockReturnValue("/writing/ch-1");

    render(<Breadcrumbs />);

    const nav = screen.getByRole("navigation", { name: "Breadcrumb" });
    expect(nav).toBeTruthy();
    expect(screen.getByRole("link", { name: "Writing" }).getAttribute("href")).toBe(
      "/writing"
    );
    expect(screen.getByText("ch 1").getAttribute("aria-current")).toBe("page");
  });

  it("returns null on home", async () => {
    const { usePathname } = await import("next/navigation");
    vi.mocked(usePathname).mockReturnValue("/");

    const { container } = render(<Breadcrumbs />);
    expect(container.firstChild).toBeNull();
  });

  it("renders knowledge module crumbs", async () => {
    const { usePathname } = await import("next/navigation");
    vi.mocked(usePathname).mockReturnValue("/knowledge");

    render(<Breadcrumbs />);
    expect(screen.getByText("Knowledge").getAttribute("aria-current")).toBe("page");
  });
});
