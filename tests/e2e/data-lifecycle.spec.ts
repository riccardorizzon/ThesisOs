import { test, expect } from "./fixtures";

let cleanupProjectId: string | null = null;

test.afterEach(async ({ request }) => {
  if (!cleanupProjectId) return;
  await request.delete(`/api/projects/${cleanupProjectId}`, {
    data: { confirmation_project_id: cleanupProjectId },
  });
  cleanupProjectId = null;
});

test("owned chapters stay visible, demo copy is idempotent, and project deletion is confirmed", async ({
  page,
  request,
}) => {
  const created = await request.post("/api/projects", {
    data: { display_name: "E2E lifecycle thesis" },
  });
  expect(created.status()).toBe(201);
  const project = (await created.json()) as { id: string };
  cleanupProjectId = project.id;

  for (const title of ["Prova", "Craftsmanship"]) {
    const chapter = await request.post("/api/chapters", {
      data: { project_id: project.id, title },
    });
    expect(chapter.status()).toBe(201);
  }

  const firstCopy = await request.post(
    `/api/chapters/copy-demo-structure?project_id=${project.id}`
  );
  expect(firstCopy.status()).toBe(201);
  expect((await firstCopy.json()).created).toHaveLength(5);
  const secondCopy = await request.post(
    `/api/chapters/copy-demo-structure?project_id=${project.id}`
  );
  expect(secondCopy.status()).toBe(201);
  expect((await secondCopy.json()).created).toHaveLength(0);

  await page.goto("/");
  await page.evaluate((projectId) => {
    localStorage.setItem("thesisos:active-project-id", projectId);
    localStorage.setItem("thesisos:last-personal-project-id", projectId);
    localStorage.setItem("thesisos:workspace-mode", "personal");
    document.cookie = `thesisos-active-project-id=${projectId}; path=/`;
    document.cookie = "thesisos-workspace-mode=personal; path=/";
  }, project.id);

  await page.goto("/writing");
  await expect(page.getByText("Prova", { exact: true })).toBeVisible();
  await expect(page.getByText("Craftsmanship", { exact: true })).toBeVisible();
  await expect(page.getByText("Introduzione", { exact: true })).toBeVisible();

  await page.goto("/settings");
  await page
    .getByRole("button", { name: "Elimina definitivamente questa tesi" })
    .click();
  await page
    .getByLabel(`Digita ${project.id} per confermare`)
    .fill(project.id);
  await page
    .getByRole("button", { name: "Conferma eliminazione definitiva" })
    .click();
  await expect(page).toHaveURL("/");
  cleanupProjectId = null;

  const projects = await request.get("/api/projects");
  const items = ((await projects.json()) as { items: { id: string }[] }).items;
  expect(items.some((item) => item.id === project.id)).toBe(false);
});

test("the default thesis never exposes project deletion", async ({ page }) => {
  await page.goto("/");
  await page.evaluate(() => {
    localStorage.setItem("thesisos:active-project-id", "thesis-agent");
    localStorage.setItem("thesisos:workspace-mode", "personal");
    document.cookie = "thesisos-active-project-id=thesis-agent; path=/";
  });

  await page.goto("/settings");
  await expect(
    page.getByRole("button", { name: "Elimina definitivamente questa tesi" })
  ).toHaveCount(0);
});
