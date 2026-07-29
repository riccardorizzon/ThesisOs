/**
 * Live VM smoke — Writing panel action loop + SSE ingress.
 * Runs on the VM (127.0.0.1); no operator browser access required.
 *
 * Prefer nginx :8080 for UI (unbuffered /api). Backend :8000 for direct API.
 */
import { test, expect } from "./fixtures";

const PROJECT_ID = "thesis-agent";
const CHAPTER_ID = "e053a6bd-64fa-435f-9193-87c9709616f3";
const API_BASE = process.env.E2E_API_BASE_URL ?? "http://127.0.0.1:8000";
/** nginx docker ingress — same-origin UI + unbuffered SSE */
const UI_BASE =
  process.env.PLAYWRIGHT_UI_BASE_URL ??
  process.env.PLAYWRIGHT_BASE_URL ??
  "http://127.0.0.1:8080";

async function seedThesisAgentProject(page: import("@playwright/test").Page) {
  await page.goto(UI_BASE + "/");
  await page.evaluate((projectId) => {
    localStorage.setItem("thesisos:active-project-id", projectId);
    localStorage.setItem("thesisos:last-personal-project-id", projectId);
    localStorage.setItem("thesisos:workspace-mode", "personal");
    document.cookie = `thesisos-active-project-id=${projectId}; path=/`;
    document.cookie = "thesisos-workspace-mode=personal; path=/";
  }, PROJECT_ID);
}

function parseSseBody(body: string) {
  const steps = (body.match(/^event: step$/gm) ?? []).length;
  const tokens = (body.match(/^event: token$/gm) ?? []).length;
  const done = /^event: done$/m.test(body);
  const draftIdx = body.indexOf('"draft"');
  const draftLen = draftIdx >= 0 ? body.length - draftIdx : 0;
  return { steps, tokens, done, draftLen };
}

test.describe("Writing action loop @ui", () => {
  test("API: verify loop returns step events then draft (live Vertex)", async ({
    request,
  }) => {
    test.setTimeout(180_000);
    const res = await request.post(`${API_BASE}/writing/actions`, {
      data: {
        action: "verify",
        project_id: PROJECT_ID,
        chapter_id: CHAPTER_ID,
        chapter_content:
          "Il processo creativo nel design può essere letto come soluzione di problemi (Löbach, flow).",
      },
      timeout: 170_000,
    });
    expect(res.ok()).toBeTruthy();
    const parsed = parseSseBody(await res.text());
    expect(parsed.steps).toBeGreaterThanOrEqual(1);
    expect(parsed.tokens).toBeGreaterThan(0);
    expect(parsed.done).toBe(true);
    expect(parsed.draftLen).toBeGreaterThan(50);
  });

  test("API: find-sources loop returns multiple searches", async ({ request }) => {
    test.setTimeout(180_000);
    const res = await request.post(`${API_BASE}/writing/actions`, {
      data: {
        action: "find-sources",
        project_id: PROJECT_ID,
        chapter_content: "artigianato intellettuale Löbach flow",
      },
      timeout: 170_000,
    });
    expect(res.ok()).toBeTruthy();
    const parsed = parseSseBody(await res.text());
    expect(parsed.steps).toBeGreaterThanOrEqual(1);
    expect(parsed.done).toBe(true);
  });

  test("API: rewrite uses legacy path (no step events)", async ({ request }) => {
    test.setTimeout(180_000);
    const res = await request.post(`${API_BASE}/writing/actions`, {
      data: {
        action: "rewrite",
        project_id: PROJECT_ID,
        selection_text: "Passaggio da riscrivere in registro accademico.",
        chapter_content: "Capitolo di prova.",
      },
      timeout: 170_000,
    });
    expect(res.ok()).toBeTruthy();
    const body = await res.text();
    expect(body).not.toMatch(/^event: step$/m);
    expect(parseSseBody(body).done).toBe(true);
  });

  test("nginx /api: verify SSE streams step then done (unbuffered)", async ({
    request,
  }) => {
    test.setTimeout(180_000);
    const res = await request.post(`${UI_BASE}/api/writing/actions`, {
      data: {
        action: "verify",
        project_id: PROJECT_ID,
        chapter_content: "Löbach flow artigianato intellettuale nginx ingress.",
      },
      timeout: 170_000,
    });
    expect(res.ok(), `nginx status ${res.status()}`).toBeTruthy();
    const parsed = parseSseBody(await res.text());
    expect(parsed.steps).toBeGreaterThanOrEqual(1);
    expect(parsed.done).toBe(true);
  });

  test("UI panel via nginx: Verifica shows loop steps and draft", async ({
    page,
  }) => {
    test.setTimeout(180_000);
    await seedThesisAgentProject(page);
    await page.goto(`${UI_BASE}/writing/${CHAPTER_ID}`);
    await expect(page.getByTestId("writing-ai-panel")).toBeVisible({
      timeout: 30_000,
    });
    await expect(page.getByTestId("context-summary")).toBeVisible({
      timeout: 30_000,
    });

    await page.getByRole("button", { name: /^Verifica/i }).click();

    await expect(page.getByTestId("ai-loop-steps")).toBeVisible({
      timeout: 90_000,
    });
    await expect(page.getByTestId("ai-stream-output")).not.toHaveText(
      /Risposta interrotta/i
    );
    await expect(page.getByTestId("ai-stream-output")).not.toBeEmpty({
      timeout: 120_000,
    });
    // Citation enforcement may block Applica until override — that is product behavior.
    const override = page.getByTestId("applica-override-button");
    if (await override.isVisible().catch(() => false)) {
      await override.click();
    }
    await expect(page.getByTestId("applica-button")).toBeEnabled({
      timeout: 15_000,
    });
  });
});
