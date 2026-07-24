import { test, expect } from "./fixtures";

test.describe("browser API boundary", () => {
  test("keeps legacy UI redirects separate from /api", async ({ request }) => {
    const legacy = await request.get("/chat", { maxRedirects: 0 });
    expect(legacy.status()).toBe(307);
    expect(legacy.headers().location).toBe("/ai");

    const documents = await request.get(
      "/api/documents?project_id=thesis-agent"
    );
    expect(documents.status()).toBe(200);
    expect(documents.headers()["content-type"]).toContain("application/json");

    const memory = await request.get("/api/memory?project_id=thesis-agent");
    expect(memory.status()).toBe(200);
    expect(memory.headers()["content-type"]).toContain("application/json");
  });

  test("forwards chat requests to FastAPI instead of the /ai page", async ({
    request,
  }) => {
    const response = await request.post("/api/chat", { data: {} });

    expect(response.status()).toBe(422);
    expect(response.headers()["content-type"]).toContain("application/json");
    expect(await response.json()).toEqual(
      expect.objectContaining({ detail: expect.any(Array) })
    );
  });

  test("the chat UI streams from /api/chat", async ({ page }) => {
    let requestedPath = "";
    await page.route("**/api/chat", async (route) => {
      requestedPath = new URL(route.request().url()).pathname;
      await route.fulfill({
        status: 200,
        contentType: "text/event-stream",
        body:
          'event: token\r\ndata: {"text":"Risposta dal namespace API"}\r\n\r\n' +
          'event: done\r\ndata: {"conversation_id":"qa-conversation","message_id":"qa-message","usage":{}}\r\n\r\n',
      });
    });

    await page.goto("/");
    await page.getByPlaceholder("Scrivi un messaggio…").fill("Ciao");
    await page.getByRole("button", { name: "Invia" }).click();

    await expect(page.getByText("Risposta dal namespace API")).toBeVisible();
    expect(requestedPath).toBe("/api/chat");
  });
});
