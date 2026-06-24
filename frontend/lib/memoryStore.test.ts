import { describe, expect, it, vi, beforeEach } from "vitest";

import * as client from "@/lib/memoryClient";
import { useMemoryStore } from "@/lib/memoryStore";

describe("memoryStore", () => {
  beforeEach(() => {
    useMemoryStore.setState({
      items: [],
      selected: null,
      versions: [],
      loading: false,
      error: null,
      errorCode: null,
      errorStatus: null,
      listQuery: "",
    });
    vi.restoreAllMocks();
  });

  it("fetchList loads items via memoryClient", async () => {
    vi.spyOn(client.memoryClient, "list").mockResolvedValue([
      {
        id: "1",
        kind: "concept",
        title: "X",
        content: "c",
        metadata: {},
        key: null,
        pinned: false,
        source: "user",
        version: 1,
        created_at: "2026-06-24T10:00:00Z",
        updated_at: "2026-06-24T10:00:00Z",
      },
    ]);

    await useMemoryStore.getState().fetchList();
    expect(useMemoryStore.getState().items).toHaveLength(1);
  });

  it("update surfaces write_conflict from client", async () => {
    vi.spyOn(client.memoryClient, "update").mockRejectedValue(
      new client.MemoryApiError(409, "write_conflict", "stale"),
    );

    await expect(
      useMemoryStore.getState().update("1", { expected_version: 1, content: "x" }),
    ).rejects.toBeInstanceOf(client.MemoryApiError);

    expect(useMemoryStore.getState().errorCode).toBe("write_conflict");
    expect(useMemoryStore.getState().errorStatus).toBe(409);
  });

  it("remove surfaces cannot_delete_singleton", async () => {
    vi.spyOn(client.memoryClient, "delete").mockRejectedValue(
      new client.MemoryApiError(400, "cannot_delete_singleton", "no"),
    );

    await expect(useMemoryStore.getState().remove("1")).rejects.toBeInstanceOf(client.MemoryApiError);
    expect(useMemoryStore.getState().errorStatus).toBe(400);
  });
});
