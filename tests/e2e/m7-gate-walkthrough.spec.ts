import { test, expect } from "@playwright/test";

const API = process.env.E2E_API_BASE_URL ?? "http://127.0.0.1:8001";
const PROJECT = "thesis-agent";

test.describe("M7 gate walkthrough G5 G6 G9 G10", () => {
  test("G10 — legacy redirects resolve", async ({ page }) => {
    await page.goto("/workspace");
    await expect(page).toHaveURL(/\/writing/);
    await expect(page.getByTestId("writing-workspace")).toBeVisible();

    await page.goto("/chat");
    await expect(page).toHaveURL(/\/ai/);
    await expect(page.getByTestId("ai-chat-view")).toBeVisible();
  });

  test("G9 — BibTeX export from Sources UI", async ({ page }) => {
    await page.goto("/sources");
    await expect(page.getByTestId("bibliography-export-bar")).toBeVisible();
    const [download] = await Promise.all([
      page.waitForEvent("download"),
      page.getByRole("button", { name: "Esporta BibTeX" }).click(),
    ]);
    const path = await download.path();
    expect(path).toBeTruthy();
    const content = await download.createReadStream();
    let text = "";
    if (content) {
      for await (const chunk of content) text += chunk.toString();
    }
    expect(text).toContain("@book{");
    expect(text).toContain("Benjamin");
    expect(text).not.toContain("Barthes");
  });

  test("G5 — search from writing source picker", async ({ page, request }) => {
    let chapterId: string | null = null;
    const chapters = await request.get(`${API}/chapters`);
    if (chapters.ok()) {
      const items = (await chapters.json()) as Array<{ id: string }>;
      chapterId = items[0]?.id ?? null;
    }
    if (!chapterId) {
      const created = await request.post(`${API}/chapters`, {
        data: { title: "G5 walkthrough", content_md: "# G5\n\nPicker search." },
      });
      expect(created.ok()).toBeTruthy();
      chapterId = ((await created.json()) as { id: string }).id;
    }

    await page.goto(`/writing/${chapterId}`);
    await expect(page.getByTestId("writing-workspace")).toBeVisible();
    const coachSkip = page.getByTestId("coach-mark-skip");
    if (await coachSkip.isVisible().catch(() => false)) {
      await coachSkip.click();
    }
    const citeButton = page.getByRole("button", { name: "Cita", exact: true });
    await expect(citeButton).toBeEnabled({ timeout: 15_000 });
    await citeButton.click();
    await expect(page.getByTestId("source-picker-modal")).toBeVisible();
    await page.getByTestId("source-picker-search").fill("Benjamin");
    await expect(page.getByTestId("source-picker-row-benjamin-opera-arte")).toBeVisible({
      timeout: 15_000,
    });
  });

  test("G6 — chat persists across reload", async ({ page, request }) => {
    const title = `G6 walkthrough ${Date.now()}`;
    const conv = await request.post(`${API}/conversations`, {
      data: { project_id: PROJECT, title },
    });
    expect(conv.ok()).toBeTruthy();
    const { id: convId } = (await conv.json()) as { id: string };

    await page.goto("/ai");
    await expect(page.getByTestId("ai-chat-view")).toBeVisible();
    await expect(page.getByTestId(`conversation-item-${convId}`)).toBeVisible({
      timeout: 15_000,
    });

    await page.reload();
    await expect(page.getByTestId(`conversation-item-${convId}`)).toBeVisible({
      timeout: 15_000,
    });

    await page.getByTestId(`conversation-item-${convId}`).click();
    await expect(page).toHaveURL(new RegExp(`conversation=${convId}`));
  });
});
