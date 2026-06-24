import { describe, expect, it, vi, beforeEach } from "vitest";

import { MemoryApiError, memoryClient, memoryDisplayTitle } from "@/lib/memoryClient";

describe("memoryClient", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("lists memories with q param", async () => {
    const fetchMock = vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [{ id: "1", kind: "concept", content: "thesis notes", version: 1 }],
    } as Response);

    const rows = await memoryClient.list({ q: "thesis" });
    expect(rows).toHaveLength(1);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/memory?q=thesis"),
      expect.objectContaining({ cache: "no-store" }),
    );
  });

  it("maps 409 write_conflict", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue({
      ok: false,
      status: 409,
      statusText: "Conflict",
      json: async () => ({ code: "write_conflict", message: "stale version" }),
    } as Response);

    await expect(
      memoryClient.update("id", { expected_version: 1, content: "x" }),
    ).rejects.toMatchObject({ status: 409, code: "write_conflict" });
  });

  it("maps 404 memory_not_found", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue({
      ok: false,
      status: 404,
      statusText: "Not Found",
      json: async () => ({ code: "memory_not_found", message: "missing" }),
    } as Response);

    await expect(memoryClient.get("missing")).rejects.toMatchObject({
      status: 404,
      code: "memory_not_found",
    });
  });

  it("maps 400 cannot_delete_singleton", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue({
      ok: false,
      status: 400,
      statusText: "Bad Request",
      json: async () => ({ code: "cannot_delete_singleton", message: "no" }),
    } as Response);

    await expect(memoryClient.delete("id")).rejects.toMatchObject({
      status: 400,
      code: "cannot_delete_singleton",
    });
  });

  it("create posts JSON body", async () => {
    const fetchMock = vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => ({ id: "new", kind: "concept", content: "body", version: 1 }),
    } as Response);

    await memoryClient.create({ kind: "concept", content: "body" });
    expect(fetchMock.mock.calls[0][1]?.method).toBe("POST");
  });

  it("memoryDisplayTitle prefers title", () => {
    expect(memoryDisplayTitle({ title: "T", key: null, content: "c" })).toBe("T");
  });
});

describe("MemoryApiError", () => {
  it("carries status and code", () => {
    const err = new MemoryApiError(409, "write_conflict", "conflict");
    expect(err).toBeInstanceOf(Error);
    expect(err.status).toBe(409);
    expect(err.code).toBe("write_conflict");
  });
});
