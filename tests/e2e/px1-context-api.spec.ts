import { test, expect } from "@playwright/test";

const API_BASE = process.env.E2E_API_BASE_URL ?? "http://127.0.0.1:8001";
const PROJECT_ID = "thesis-agent";

async function contextEndpointReady(
  request: import("@playwright/test").APIRequestContext
): Promise<boolean> {
  const response = await request.get(
    `${API_BASE}/projects/${PROJECT_ID}/context?surface=home`
  );
  return response.ok();
}

test.describe("PX1 Context API smoke @api", () => {
  test.beforeAll(async ({ request }) => {
    const ready = await contextEndpointReady(request);
    test.skip(
      !ready,
      `Context API not ready at ${API_BASE} — ensure Postgres (make up db) and workspace backend are available`
    );
  });

  test("GET /projects/{id}/context returns valid ContextPacket", async ({
    request,
  }) => {
    const response = await request.get(
      `${API_BASE}/projects/${PROJECT_ID}/context?surface=writing`
    );
    expect(response.ok()).toBeTruthy();

    const body = await response.json();
    expect(body.schema_version).toBeTruthy();
    expect(body.project_context).toMatchObject({
      project_id: PROJECT_ID,
    });
    expect(body.presentation).toMatchObject({ surface: "writing" });
    expect(body.project).toMatchObject({
      title: expect.any(String),
      phase: expect.any(String),
      progress_pct: expect.any(Number),
    });
    expect(Array.isArray(body.decisions)).toBe(true);
    expect(Array.isArray(body.corpus_constraints)).toBe(true);
  });

  test("Context API home surface matches schema", async ({ request }) => {
    const response = await request.get(
      `${API_BASE}/projects/${PROJECT_ID}/context?surface=home`
    );
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.presentation.surface).toBe("home");
  });
});
