import { test, expect } from "@playwright/test";

let cleanupProjectId: string | null = null;

test.afterEach(async ({ request }) => {
  if (!cleanupProjectId) return;
  await request.delete(`/api/projects/${cleanupProjectId}`, {
    data: { confirmation_project_id: cleanupProjectId },
  });
  cleanupProjectId = null;
});

test("first-use writing remains actionable and incomplete research is hidden", async ({
  context,
  page,
  request,
}) => {
  const created = await request.post("/api/projects", {
    data: { display_name: "E2E UX thesis" },
  });
  const project = (await created.json()) as { id: string };
  cleanupProjectId = project.id;

  await context.addInitScript((projectId) => {
    localStorage.setItem("thesisos:welcome-complete", "1");
    localStorage.setItem("thesisos:workspace-mode", "personal");
    localStorage.setItem("thesisos:active-project-id", projectId);
    localStorage.removeItem("thesisos-onboarding-m7");
    document.cookie = "thesisos-welcome-complete=1; path=/";
    document.cookie = "thesisos-workspace-mode=personal; path=/";
    document.cookie = `thesisos-active-project-id=${projectId}; path=/`;
  }, project.id);

  await page.goto("/writing");
  await expect(page.getByTestId("coach-mark-backdrop")).toBeVisible();
  await page.getByTestId("writing-create-chapter-cta").click();
  await expect(page.getByTestId("writing-create-chapter-form")).toBeVisible();
  await expect(page.getByTestId("session-chip")).toContainText("<1m");

  await page.goto("/research");
  await expect(page.getByText("Esplorazione guidata")).toHaveCount(0);
  await page.goto("/research/guided");
  await expect(page).toHaveURL(/\/research$/);
});
