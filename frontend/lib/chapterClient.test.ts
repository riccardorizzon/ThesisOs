import { beforeEach, describe, expect, it, vi } from "vitest";

import { ChapterApiError, chapterClient } from "@/lib/chapterClient";

describe("chapterClient", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("lists with project_id/parent_id/q params", async () => {
    const fetchMock = vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [{ id: "1" }],
    } as Response);

    await chapterClient.list({ project_id: "proj-a", parent_id: "p1", q: "intro" });
    const url = fetchMock.mock.calls[0][0] as string;
    expect(url).toContain("/chapters?");
    expect(url).toContain("project_id=proj-a");
    expect(url).toContain("parent_id=p1");
    expect(url).toContain("q=intro");
  });

  it("defaults project_id when list params omit it", async () => {
    const fetchMock = vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [],
    } as Response);

    await chapterClient.list({ q: "intro" });
    const url = fetchMock.mock.calls[0][0] as string;
    expect(url).toContain("project_id=");
  });

  it("creates via JSON POST", async () => {
    const fetchMock = vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => ({ id: "ch1", title: "Intro" }),
    } as Response);

    const ch = await chapterClient.create({ title: "Intro" });
    expect(ch.id).toBe("ch1");
    const init = fetchMock.mock.calls[0][1] as RequestInit;
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body as string).title).toBe("Intro");
  });

  it("update PATCHes with expected_version", async () => {
    const fetchMock = vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ id: "ch1", version: 2 }),
    } as Response);

    const ch = await chapterClient.update("ch1", { content_md: "hi", expected_version: 1 });
    expect(ch.version).toBe(2);
    const init = fetchMock.mock.calls[0][1] as RequestInit;
    expect(init.method).toBe("PATCH");
    expect(JSON.parse(init.body as string).expected_version).toBe(1);
  });

  it("handles write conflict helper via ChapterApiError", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue({
      ok: false,
      status: 409,
      statusText: "Conflict",
      json: async () => ({
        code: "write_conflict",
        message: "Capitolo modificato altrove",
      }),
    } as Response);

    await expect(
      chapterClient.update("ch1", { content_md: "x", expected_version: 1 }),
    ).rejects.toMatchObject({
      status: 409,
      code: "write_conflict",
      message: "Capitolo modificato altrove",
    });
  });

  it("maps 404 chapter_not_found", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue({
      ok: false,
      status: 404,
      statusText: "Not Found",
      json: async () => ({ code: "chapter_not_found", message: "missing" }),
    } as Response);

    await expect(chapterClient.get("missing")).rejects.toMatchObject({
      status: 404,
      code: "chapter_not_found",
    });
  });

  it("lists versions", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [{ chapter_id: "ch1", version: 1, change_kind: "WRITE" }],
    } as Response);

    const versions = await chapterClient.listVersions("ch1");
    expect(versions[0].change_kind).toBe("WRITE");
  });

  it("exportMarkdown fetches markdown blob", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      status: 200,
      blob: async () => new Blob(["# Hello"], { type: "text/markdown" }),
    } as Response);

    const blob = await chapterClient.exportMarkdown("ch1");
    expect(blob.type).toContain("markdown");
    const url = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0][0] as string;
    expect(url).toContain("/export/chapters/ch1.md");
  });
});

describe("ChapterApiError", () => {
  it("carries status and code", () => {
    const err = new ChapterApiError(409, "write_conflict", "conflict");
    expect(err).toBeInstanceOf(Error);
    expect(err.status).toBe(409);
    expect(err.code).toBe("write_conflict");
  });
});
