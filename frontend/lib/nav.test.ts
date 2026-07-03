import { describe, expect, it } from "vitest";
import {
  PRIMARY_NAV,
  buildBreadcrumbs,
  formatBreadcrumbLabel,
  isNavActive,
  shouldShowBreadcrumbs,
} from "./nav";

describe("PRIMARY_NAV", () => {
  it("matches ADR-0036 sidebar (six modules + Settings)", () => {
    const labels = PRIMARY_NAV.map((r) => r.label);
    expect(labels).toEqual([
      "Home",
      "Research",
      "Writing",
      "Sources",
      "Knowledge",
      "Settings",
    ]);
  });

  it("has exactly one settings route", () => {
    expect(PRIMARY_NAV.filter((r) => r.group === "settings")).toHaveLength(1);
    expect(PRIMARY_NAV.filter((r) => r.group === "primary")).toHaveLength(5);
  });
});

describe("isNavActive", () => {
  it("matches home exactly", () => {
    expect(isNavActive("/", "/")).toBe(true);
    expect(isNavActive("/writing", "/")).toBe(false);
  });

  it("matches nested routes", () => {
    expect(isNavActive("/writing/ch-1", "/writing")).toBe(true);
    expect(isNavActive("/writing-old", "/writing")).toBe(false);
  });
});

describe("formatBreadcrumbLabel", () => {
  it("replaces hyphens with spaces", () => {
    expect(formatBreadcrumbLabel("stigmata-framework")).toBe(
      "stigmata framework"
    );
  });
});

describe("buildBreadcrumbs", () => {
  it("returns empty trail on home", () => {
    expect(buildBreadcrumbs("/")).toEqual([]);
  });

  it("builds module root crumbs", () => {
    expect(buildBreadcrumbs("/writing")).toEqual([{ label: "Writing" }]);
    expect(buildBreadcrumbs("/sources")).toEqual([{ label: "Sources" }]);
    expect(buildBreadcrumbs("/knowledge")).toEqual([{ label: "Knowledge" }]);
  });

  it("builds nested dynamic crumbs with parent link", () => {
    expect(buildBreadcrumbs("/writing/ch-1")).toEqual([
      { label: "Writing", href: "/writing" },
      { label: "ch 1" },
    ]);
    expect(buildBreadcrumbs("/sources/benjamin-1935")).toEqual([
      { label: "Sources", href: "/sources" },
      { label: "benjamin 1935" },
    ]);
    expect(buildBreadcrumbs("/knowledge/stigmata")).toEqual([
      { label: "Knowledge", href: "/knowledge" },
      { label: "stigmata" },
    ]);
  });

  it("builds research nested crumbs", () => {
    expect(buildBreadcrumbs("/research/color-theory")).toEqual([
      { label: "Research", href: "/research" },
      { label: "color theory" },
    ]);
  });

  it("handles settings route", () => {
    expect(buildBreadcrumbs("/settings")).toEqual([{ label: "Settings" }]);
  });
});

describe("shouldShowBreadcrumbs", () => {
  it("hides on home", () => {
    expect(shouldShowBreadcrumbs("/")).toBe(false);
  });

  it("shows on module routes", () => {
    expect(shouldShowBreadcrumbs("/writing")).toBe(true);
    expect(shouldShowBreadcrumbs("/knowledge/concept-1")).toBe(true);
  });
});
