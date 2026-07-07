import { test, expect } from "@playwright/test";

const API_BASE = process.env.E2E_API_BASE_URL ?? "http://127.0.0.1:8001";
const PROJECT_ID = "thesis-agent";

test.describe("M7 workflow @m7", () => {
  test("Home surfaces import CTA and primary navigation", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Home", level: 1 })).toBeVisible();
    await expect(page.getByRole("link", { name: /Importa documento/i })).toBeVisible();
    const nav = page.getByRole("navigation", { name: "Primary" });
    for (const label of ["Home", "Research", "Writing", "Sources", "Knowledge", "Settings"]) {
      await expect(nav.getByRole("link", { name: label })).toBeVisible();
    }
  });

  test("Upload UI renders import form", async ({ page }) => {
    await page.goto("/sources/upload");
    await expect(page.getByRole("heading", { name: /Importa documento/i })).toBeVisible();
    await expect(page.getByTestId("source-upload-form")).toBeVisible();
    await expect(page.getByTestId("source-file-input")).toBeVisible();
  });

  test("Sources page loads DB-backed library and search", async ({ page }) => {
    await page.goto("/sources");
    await expect(page.getByRole("heading", { name: "Sources", level: 1 })).toBeVisible();
    await expect(page.getByTestId("bibliography-export-bar")).toBeVisible();
    await expect(page.getByTestId("sources-search-input")).toBeVisible();
    await expect(page.getByRole("link", { name: /Benjamin/i })).toBeVisible();
    await page.getByTestId("sources-search-input").fill("Benjamin");
    await expect(page.getByRole("link", { name: /Benjamin/i })).toBeVisible();
  });

  test("Knowledge explorer loads from API", async ({ page }) => {
    await page.goto("/knowledge");
    await expect(page.getByRole("heading", { name: "Knowledge", level: 1 })).toBeVisible();
    await expect(page.getByTestId("knowledge-filter-rail")).toBeVisible();
    await expect(page.getByPlaceholder(/Cerca concetti/i)).toBeVisible();
    await expect(page.getByTestId("knowledge-card-aura")).toBeVisible({ timeout: 15_000 });
  });

  test("Writing workspace shell renders", async ({ page }) => {
    await page.goto("/writing");
    await expect(page.getByTestId("writing-workspace")).toBeVisible();
    await expect(page.getByTestId("context-summary")).toBeVisible();
  });

  test("Review workspace loads", async ({ page }) => {
    await page.goto("/review");
    await expect(page.getByRole("heading", { name: "Revisione", level: 1 })).toBeVisible({
      timeout: 15_000,
    });
    await expect(page.getByTestId("context-bar")).toBeVisible();
  });

  test("Chat view loads conversation list from API", async ({ page }) => {
    await page.goto("/ai");
    await expect(page.getByTestId("ai-chat-view")).toBeVisible();
    await expect(page.getByTestId("conversation-list")).toBeVisible({ timeout: 15_000 });
  });

  test("legacy /workspace redirects to Writing", async ({ page }) => {
    await page.goto("/workspace");
    await expect(page).toHaveURL(/\/writing/);
    await expect(page.getByTestId("writing-workspace")).toBeVisible();
  });

  test("Context API and export endpoints respond", async ({ request }) => {
    const context = await request.get(
      `${API_BASE}/projects/${PROJECT_ID}/context?surface=home`
    );
    expect(context.ok()).toBeTruthy();

    const bib = await request.get(
      `${API_BASE}/projects/${PROJECT_ID}/sources/bibliography/export`
    );
    expect(bib.ok()).toBeTruthy();
    const bibText = await bib.text();
    expect(bibText).toContain("@book{");
    expect(bibText).toContain("Benjamin");
  });
});
