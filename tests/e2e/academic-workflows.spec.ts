import { test, expect } from "./fixtures";

let cleanupProjectId: string | null = null;

test.afterEach(async ({ request }) => {
  if (!cleanupProjectId) return;
  await request.delete(`/api/projects/${cleanupProjectId}`, {
    data: { confirmation_project_id: cleanupProjectId },
  });
  cleanupProjectId = null;
});

test("upload, bibliography, citations, and Knowledge Notes work in one thesis", async ({
  page,
  request,
}) => {
  const created = await request.post("/api/projects", {
    data: { display_name: "E2E academic thesis" },
  });
  expect(created.status()).toBe(201);
  const project = (await created.json()) as { id: string };
  cleanupProjectId = project.id;

  await page.goto("/");
  await page.evaluate((projectId) => {
    localStorage.setItem("thesisos:active-project-id", projectId);
    localStorage.setItem("thesisos:last-personal-project-id", projectId);
    localStorage.setItem("thesisos:workspace-mode", "personal");
    document.cookie = `thesisos-active-project-id=${projectId}; path=/`;
    document.cookie = "thesisos-workspace-mode=personal; path=/";
  }, project.id);

  await page.goto("/sources/upload");
  await page.getByTestId("source-file-input").setInputFiles({
    name: "metodo.md",
    mimeType: "text/markdown",
    buffer: Buffer.from(
      "# Metodo\n\nLa triangolazione confronta osservazioni e interviste."
    ),
  });
  const textInputs = page.locator("form input:not([type=file])");
  await textInputs.nth(0).fill("Metodo qualitativo");
  await textInputs.nth(1).fill("Mario Rossi");
  await textInputs.nth(2).fill("it");
  const uploadResponsePromise = page.waitForResponse(
    (response) =>
      response.url().endsWith("/api/upload") &&
      response.request().method() === "POST"
  );
  await page.getByRole("button", { name: "Aggiungi fonte" }).click();
  const uploadResponse = await uploadResponsePromise;
  expect(uploadResponse.status()).toBe(201);
  expect((await uploadResponse.json()).project_id).toBe(project.id);
  const scopedSources = await request.get(
    `/api/projects/${project.id}/sources`
  );
  expect(
    ((await scopedSources.json()) as { sources: { title: string }[] }).sources
      .map((source) => source.title)
  ).toContain("Metodo qualitativo");
  await expect(page).toHaveURL(/\/sources\?document=/);
  await expect(page.getByText("Metodo qualitativo")).toBeVisible();

  await page
    .getByRole("button", { name: "Aggiungi alla bibliografia" })
    .click();
  await expect(page.getByText("Aggiunta alla bibliografia")).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Esporta BibTeX" })
  ).toBeEnabled();

  const bibliography = await request.get(
    `/api/projects/${project.id}/sources/bibliography/export`
  );
  expect(bibliography.status()).toBe(200);
  expect(await bibliography.text()).toContain("Mario Rossi");
  expect(await (await request.get(
    `/api/projects/${project.id}/sources/bibliography/export`
  )).text()).toContain("n.d.");

  const linkedCitation = await request.post("/api/citations/validate", {
    data: {
      project_id: project.id,
      text: "La fonte è pertinente (Rossi, n.d.).",
    },
  });
  expect(linkedCitation.status()).toBe(200);
  expect((await linkedCitation.json()).blocking).toBe(false);

  const unlinkedCitation = await request.post("/api/citations/validate", {
    data: {
      project_id: project.id,
      text: "Fonte inventata (FantomaAutore, 2050).",
    },
  });
  expect((await unlinkedCitation.json()).blocking).toBe(true);

  const invalidPdf = await request.post("/api/upload", {
    multipart: {
      project_id: project.id,
      file: {
        name: "fake.pdf",
        mimeType: "application/pdf",
        buffer: Buffer.from("plain text"),
      },
    },
  });
  expect(invalidPdf.status()).toBe(415);
  expect((await invalidPdf.json()).code).toBe("invalid_file_content");

  await page.goto("/knowledge?view=notes");
  await page.getByRole("button", { name: "Nuova nota" }).click();
  await page.getByLabel("Titolo nota").fill("Nota di ricerca");
  await page.getByLabel("Contenuto nota").fill("Confrontare le interviste.");
  await page.getByLabel("Includi nel contesto AI").check();
  await page.getByRole("button", { name: "Salva nota" }).click();
  await expect(page.getByRole("button", { name: "Nota di ricerca" })).toBeVisible();
});
