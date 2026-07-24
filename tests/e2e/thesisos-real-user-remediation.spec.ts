import { test, expect } from "./fixtures";

test.setTimeout(600_000);

let cleanupProjectId: string | null = null;

test.afterEach(async ({ request }) => {
  if (!cleanupProjectId) return;
  await request.delete(`/api/projects/${cleanupProjectId}`, {
    data: { confirmation_project_id: cleanupProjectId },
  });
  cleanupProjectId = null;
});

function donePayload(stream: string): Record<string, unknown> {
  const match = stream.match(/event: done\r?\ndata: (.+?)(?:\r?\n){2}/);
  if (!match?.[1]) throw new Error(`SSE stream has no done payload: ${stream}`);
  return JSON.parse(match[1]) as Record<string, unknown>;
}

test("real user can research, write, revise, and converse in an isolated thesis", async ({
  page,
  request,
}) => {
  const created = await request.post("/api/projects", {
    data: { display_name: "E2E real-user thesis" },
  });
  expect(created.status()).toBe(201);
  const project = (await created.json()) as { id: string };
  cleanupProjectId = project.id;

  await page.goto("/");
  await page.evaluate((projectId) => {
    localStorage.setItem("thesisos:active-project-id", projectId);
    localStorage.setItem("thesisos:last-personal-project-id", projectId);
    localStorage.setItem("thesisos:workspace-mode", "personal");
    localStorage.setItem(
      "thesisos-onboarding-m7",
      JSON.stringify({ dismissed: true, completedSteps: [1, 2, 3, 4, 5] })
    );
    document.cookie = `thesisos-active-project-id=${projectId}; path=/`;
    document.cookie = "thesisos-workspace-mode=personal; path=/";
  }, project.id);

  const upload = await request.post("/api/upload", {
    multipart: {
      project_id: project.id,
      title: "Metodologia qualitativa",
      author: "Mario Rossi",
      language: "it",
      file: {
        name: "metodologia.md",
        mimeType: "text/markdown",
        buffer: Buffer.from(
          [
            "# Metodo etnografico",
            "L’osservazione partecipante documenta le pratiche degli utenti.",
            "# Campionamento teorico",
            "I casi vengono selezionati iterativamente fino alla saturazione teorica.",
            "# Triangolazione",
            "La triangolazione combina osservazioni, interviste e documenti.",
          ].join("\n\n")
        ),
      },
    },
  });
  expect(upload.status()).toBe(201);
  const document = (await upload.json()) as { id: string };

  let documentState: {
    status: string;
    error_message?: string | null;
  } | null = null;
  for (let attempt = 0; attempt < 45; attempt += 1) {
    const response = await request.get(
      `/api/documents/${document.id}?project_id=${project.id}`
    );
    documentState = await response.json();
    if (["indexed", "failed"].includes(documentState.status)) break;
    await page.waitForTimeout(1_000);
  }
  expect(
    documentState,
    `indexing failed: ${documentState?.error_message ?? "timeout"}`
  ).toMatchObject({ status: "indexed" });

  const search = await request.post("/api/search", {
    data: {
      project_id: project.id,
      query: "Come funziona la triangolazione?",
      limit: 5,
    },
  });
  expect(search.status()).toBe(200);
  const searchBody = (await search.json()) as {
    results: { document_title: string }[];
  };
  expect(
    searchBody.results.some(
      (result) => result.document_title === "Metodologia qualitativa"
    )
  ).toBe(true);

  const chapterResponse = await request.post("/api/chapters", {
    data: { project_id: project.id, title: "Introduzione" },
  });
  const chapter = (await chapterResponse.json()) as { id: string };
  await page.goto(`/writing/${chapter.id}`);
  const editor = page.locator("textarea").first();
  const initialContent =
    "# Introduzione\n\nLa ricerca applica metodi qualitativi al design.";
  await editor.fill(initialContent);
  await expect(page.getByTestId("editor-save-indicator")).toHaveAttribute(
    "data-state",
    "saved",
    { timeout: 15_000 }
  );

  const writingAction = await request.post("/api/writing/actions", {
    data: {
      action: "expand",
      project_id: project.id,
      chapter_id: chapter.id,
      selection_text:
        "La ricerca applica metodi qualitativi al design.",
      chapter_content: initialContent,
    },
    timeout: 120_000,
  });
  expect(writingAction.status()).toBe(200);
  const writingStream = await writingAction.text();
  const writingDone = donePayload(writingStream);
  const proposed = String(writingDone.draft ?? "");
  expect(proposed.length).toBeGreaterThan(80);

  const proposal = await request.post("/api/proposals", {
    data: {
      project_id: project.id,
      chapter_id: chapter.id,
      original: initialContent,
      proposed,
      action: "expand",
      metadata: { action_label: "Espandi" },
    },
  });
  expect(proposal.status()).toBe(201);

  await page.goto("/review");
  await page.getByRole("option", { name: /Introduzione/ }).click();
  await page.getByRole("button", { name: "Accetta tutto" }).click();
  await page.getByRole("button", { name: "Conferma" }).click();
  await expect(
    page.getByText("Nessuna revisione in sospeso")
  ).toBeVisible({ timeout: 10_000 });

  const accepted = await request.get(
    `/api/chapters/${chapter.id}?project_id=${project.id}`
  );
  expect((await accepted.json()).content_md).toBe(proposed);

  const chat = await request.post("/api/chat", {
    data: {
      project_id: project.id,
      message:
        "Riassumi cosa dice il mio documento sulla triangolazione dei dati.",
    },
    timeout: 120_000,
  });
  expect(chat.status()).toBe(200);
  const chatStream = await chat.text();
  expect(chatStream).toContain("event: sources");
  expect(chatStream).toContain("Metodologia qualitativa");
  const chatDone = donePayload(chatStream);
  const conversationId = String(chatDone.conversation_id);

  const conversations = await request.get(
    `/api/conversations?project_id=${project.id}`
  );
  const thread = (
    (await conversations.json()) as {
      items: { id: string; title: string }[];
    }
  ).items.find((item) => item.id === conversationId);
  expect(thread?.title).toMatch(/^Riassumi cosa dice il mio documento/);

  const firstTurn = request.post("/api/chat", {
    data: {
      project_id: project.id,
      conversation_id: conversationId,
      message:
        "Scrivi una spiegazione articolata della triangolazione metodologica.",
    },
    timeout: 120_000,
  });
  await page.waitForTimeout(100);
  const concurrent = await request.post("/api/chat", {
    data: {
      project_id: project.id,
      conversation_id: conversationId,
      message: "Seconda richiesta simultanea",
    },
  });
  expect(concurrent.status()).toBe(409);
  expect((await concurrent.json()).code).toBe("conversation_busy");
  expect((await firstTurn).status()).toBe(200);
});
