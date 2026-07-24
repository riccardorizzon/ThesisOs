import { beforeEach, describe, expect, it, vi } from "vitest";

import { DocumentApiError, documentClient, documentDisplayTitle } from "@/lib/documentClient";

describe("documentClient", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("lists with q/status/source_type params", async () => {
    const fetchMock = vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [{ id: "1" }],
    } as Response);

    const rows = await documentClient.list({ q: "paper", status: "parsed", source_type: "pdf" });
    expect(rows).toHaveLength(1);
    const url = fetchMock.mock.calls[0][0] as string;
    expect(url).toContain("/documents?");
    expect(url).toContain("q=paper");
    expect(url).toContain("status=parsed");
    expect(url).toContain("source_type=pdf");
  });

  it("uploads via multipart FormData (no JSON content-type)", async () => {
    const fetchMock = vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => ({ id: "d1" }),
    } as Response);

    const file = new File([new Uint8Array([1, 2, 3])], "a.pdf", { type: "application/pdf" });
    await documentClient.upload({ file, title: "T" });

    const init = fetchMock.mock.calls[0][1] as RequestInit;
    expect(init.method).toBe("POST");
    expect(init.body).toBeInstanceOf(FormData);
    expect((init.body as FormData).get("title")).toBe("T");
    expect((init.headers as Record<string, string> | undefined)?.["Content-Type"]).toBeUndefined();
  });

  it("maps 404 document_not_found", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue({
      ok: false,
      status: 404,
      statusText: "Not Found",
      json: async () => ({ code: "document_not_found", message: "missing" }),
    } as Response);

    await expect(documentClient.get("missing")).rejects.toMatchObject({
      status: 404,
      code: "document_not_found",
    });
  });

  it("maps 409 write_conflict", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue({
      ok: false,
      status: 409,
      statusText: "Conflict",
      json: async () => ({ code: "write_conflict", message: "stale" }),
    } as Response);

    await expect(documentClient.update("id", { expected_version: 1 })).rejects.toMatchObject({
      status: 409,
      code: "write_conflict",
    });
  });

  it("maps 415 unsupported_format on upload", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue({
      ok: false,
      status: 415,
      statusText: "Unsupported Media Type",
      json: async () => ({ code: "unsupported_format", message: "no" }),
    } as Response);

    const file = new File([], "malware.exe");
    await expect(documentClient.upload({ file })).rejects.toMatchObject({
      status: 415,
      code: "unsupported_format",
    });
  });

  it("reparse POSTs and returns processing", async () => {
    const fetchMock = vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      status: 202,
      json: async () => ({ document_id: "d1", status: "processing" }),
    } as Response);

    const r = await documentClient.reparse("d1");
    expect(r.status).toBe("processing");
    expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe("POST");
  });

  it("maps a successful HTML response to a product-safe invalid_response error", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(
      new Response("<!DOCTYPE html><h1>Sources</h1>", {
        status: 200,
        headers: { "Content-Type": "text/html" },
      })
    );

    await expect(documentClient.list()).rejects.toMatchObject({
      status: 200,
      code: "invalid_response",
      message: "Impossibile leggere i documenti. Riprova.",
    });
  });

  it("documentDisplayTitle prefers title then filename", () => {
    expect(documentDisplayTitle({ title: "T", original_filename: "f.pdf" })).toBe("T");
    expect(documentDisplayTitle({ title: "", original_filename: "f.pdf" })).toBe("f.pdf");
  });
});

describe("DocumentApiError", () => {
  it("carries status and code", () => {
    const err = new DocumentApiError(409, "write_conflict", "conflict");
    expect(err).toBeInstanceOf(Error);
    expect(err.status).toBe(409);
    expect(err.code).toBe("write_conflict");
  });
});
