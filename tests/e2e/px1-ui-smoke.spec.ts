import { test, expect } from "./fixtures";

/** ADR-0036 INV-IA-1 — six primary modules + Settings (Review is module route, not sidebar). */
const SIDEBAR_LABELS = [
  "Home",
  "Research",
  "Writing",
  "Manoscritto",
  "Sources",
  "Knowledge",
  "Settings",
] as const;

test.describe("PX1 UI smoke @ui", () => {
  test("Home loads as default route", async ({ page }) => {
    await page.goto("/");
    await expect(
      page.getByRole("heading", { name: "Thesis Companion", level: 1 })
    ).toBeVisible();
    await expect(
      page.getByRole("main").getByText(/Riprendi il lavoro/)
    ).toBeVisible();
  });

  test("sidebar IA matches ADR-0036", async ({ page }) => {
    await page.goto("/");
    const nav = page.getByRole("navigation", { name: "Primary" });
    for (const label of SIDEBAR_LABELS) {
      await expect(nav.getByRole("link", { name: label })).toBeVisible();
    }
  });

  test("Writing workspace shell renders", async ({ page }) => {
    await page.goto("/writing");
    await expect(page.getByTestId("writing-workspace")).toBeVisible();
    await expect(page.getByTestId("writing-outline")).toBeVisible();
    await expect(page.getByTestId("context-summary")).toBeVisible();
    await expect(page.getByTestId("writing-index-status-error")).toHaveCount(0);
  });

  test("Sources shell renders for populated or empty projects", async ({ page }) => {
    await page.goto("/sources");
    await expect(page.getByRole("heading", { name: "Sources", level: 1 })).toBeVisible();
    await expect(
      page.getByRole("link", { name: "Aggiungi fonte" }).first()
    ).toBeVisible();
  });

  test("legacy /workspace redirects to Writing", async ({ page }) => {
    await page.goto("/workspace");
    await expect(page).toHaveURL(/\/writing/);
    await expect(page.getByTestId("writing-workspace")).toBeVisible();
  });
});
