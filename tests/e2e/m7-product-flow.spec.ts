import { test, expect } from "./fixtures";

const API_BASE = process.env.E2E_API_BASE_URL ?? "http://127.0.0.1:8001";
const PROJECT_ID = "thesis-agent";

test.describe("M7 product flow @m7", () => {
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
    await expect(page.getByRole("heading", { name: /Aggiungi fonte/i })).toBeVisible();
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

  test("Writing workspace shell renders with export menu", async ({ page }) => {
    await page.goto("/writing");
    await expect(page.getByTestId("writing-workspace")).toBeVisible();
    await expect(page.getByTestId("context-summary")).toBeVisible();
    await expect(page.getByTestId("export-menu")).toBeVisible();
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

    const created = await request.post(`${API_BASE}/chapters`, {
      data: { title: "E2E export", content_md: "# E2E\n\nExport smoke." },
    });
    expect(created.ok()).toBeTruthy();
    const chapter = (await created.json()) as { id: string };
    const md = await request.get(`${API_BASE}/export/chapters/${chapter.id}.md`);
    expect(md.ok()).toBeTruthy();
    expect(md.headers()["content-type"] ?? "").toContain("text/markdown");
    expect(await md.text()).toContain("Export smoke.");
  });
});
