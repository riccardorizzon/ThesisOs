/**
 * Live VM smoke — Writing panel action loop (verify / find-sources).
 * Runs against docker stack on 127.0.0.1 (operator does not need browser access).
 */
import { test, expect } from "./fixtures";

const PROJECT_ID = "thesis-agent";
/** Chapter with substantial content in demo thesis */
const CHAPTER_ID = "e053a6bd-64fa-435f-9193-87c9709616f3";

async function seedThesisAgentProject(page: import("@playwright/test").Page) {
  await page.goto("/");
  await page.evaluate((projectId) => {
    localStorage.setItem("thesisos:active-project-id", projectId);
    localStorage.setItem("thesisos:last-personal-project-id", projectId);
    localStorage.setItem("thesisos:workspace-mode", "personal");
    document.cookie = `thesisos-active-project-id=${projectId}; path=/`;
    document.cookie = "thesisos-workspace-mode=personal; path=/";
  }, PROJECT_ID);
}

test.describe("Writing action loop @ui", () => {
  test("Verifica shows loop steps then streams draft (live Vertex)", async ({ page }) => {
    test.setTimeout(180_000);

    await seedThesisAgentProject(page);
    await page.goto(`/writing/${CHAPTER_ID}`);

    await expect(page.getByTestId("writing-workspace")).toBeVisible({ timeout: 30_000 });
    await expect(page.getByTestId("writing-ai-panel")).toBeVisible({ timeout: 30_000 });
    await expect(page.getByTestId("context-summary")).toBeVisible({ timeout: 30_000 });

    const verifyBtn = page.getByRole("button", { name: /Verifica/i });
    await expect(verifyBtn).toBeEnabled({ timeout: 15_000 });

    await verifyBtn.click();

    await expect(page.getByTestId("ai-loop-steps")).toBeVisible({ timeout: 60_000 });
    await expect(page.getByTestId("ai-loop-steps")).toContainText(/search_corpus|contesto|Ricerca/i);

    await expect(page.getByTestId("ai-stream-output")).not.toBeEmpty({ timeout: 120_000 });
    await expect(page.getByTestId("applica-button")).toBeEnabled({ timeout: 10_000 });
  });

  test("Riscrivi does not show loop steps (legacy path)", async ({ page }) => {
    test.setTimeout(180_000);

    await seedThesisAgentProject(page);
    await page.goto(`/writing/${CHAPTER_ID}`);

    await expect(page.getByTestId("writing-ai-panel")).toBeVisible({ timeout: 30_000 });

    const editor = page.locator('[contenteditable="true"]').first();
    await editor.click();
    await page.keyboard.press("Control+a");
    await page.keyboard.type("Passaggio di prova per riscrittura.");

    const rewriteBtn = page.getByRole("button", { name: /Riscrivi/i });
    await expect(rewriteBtn).toBeEnabled({ timeout: 15_000 });
    await rewriteBtn.click();

    await expect(page.getByTestId("ai-stream-output")).not.toBeEmpty({ timeout: 120_000 });
    await expect(page.getByTestId("ai-loop-steps")).toHaveCount(0);
  });
});
