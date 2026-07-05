import { describe, expect, it, vi, afterEach } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { RailTabs, railTabFromShortcut } from "./RailTabs";

afterEach(() => cleanup());

describe("RailTabs", () => {
  it("renders tablist with four Italian rail tabs", () => {
    const onTabChange = vi.fn();
    render(<RailTabs activeTab="ai" onTabChange={onTabChange} />);

    const tablist = screen.getByRole("tablist", { name: "Pannello laterale scrittura" });
    expect(tablist).toBeTruthy();

    expect(screen.getByRole("tab", { name: "AI" })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByRole("tab", { name: "Contesto" })).toHaveAttribute("aria-selected", "false");
    expect(screen.getByRole("tab", { name: "Fonte" })).toHaveAttribute("aria-selected", "false");
    expect(screen.getByRole("tab", { name: "Revisione" })).toHaveAttribute("aria-selected", "false");
  });

  it("calls onTabChange when a tab is clicked", () => {
    const onTabChange = vi.fn();
    render(<RailTabs activeTab="ai" onTabChange={onTabChange} />);

    fireEvent.click(screen.getByRole("tab", { name: "Contesto" }));
    expect(onTabChange).toHaveBeenCalledWith("contesto");
  });

  it("maps shortcut digits to tab ids", () => {
    expect(railTabFromShortcut(1)).toBe("ai");
    expect(railTabFromShortcut(2)).toBe("contesto");
    expect(railTabFromShortcut(3)).toBe("fonte");
    expect(railTabFromShortcut(4)).toBe("revisione");
    expect(railTabFromShortcut(9)).toBeNull();
  });
});
