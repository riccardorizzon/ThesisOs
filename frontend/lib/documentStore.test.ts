import { beforeEach, describe, expect, it, vi } from "vitest";

import { useDocumentStore } from "@/lib/documentStore";

function reset() {
  useDocumentStore.setState({
    items: [],
    selected: null,
    chunks: [],
    versions: [],
    loading: false,
    error: null,
    errorCode: null,
    errorStatus: null,
    listQuery: "",
    statusFilter: "",
    sourceTypeFilter: "",
  });
}

describe("useDocumentStore", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    reset();
  });

  it("fetchList populates items", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [
        {
          id: "1",
          title: "A",
          author: null,
          source_type: "pdf",
          original_filename: "a.pdf",
          gcs_uri: null,
          status: "parsed",
          page_count: null,
          language: null,
          version: 1,
          parser: null,
          parsed_at: null,
          chunk_count: 3,
          error_message: null,
          metadata: {},
          created_at: "",
          updated_at: "",
        },
      ],
    } as Response);

    await useDocumentStore.getState().fetchList();
    expect(useDocumentStore.getState().items).toHaveLength(1);
    expect(useDocumentStore.getState().loading).toBe(false);
  });

  it("fetchOne 404 clears selected and records error", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue({
      ok: false,
      status: 404,
      statusText: "Not Found",
      json: async () => ({ code: "document_not_found", message: "missing" }),
    } as Response);

    await useDocumentStore.getState().fetchOne("missing");
    const s = useDocumentStore.getState();
    expect(s.selected).toBeNull();
    expect(s.errorStatus).toBe(404);
    expect(s.errorCode).toBe("document_not_found");
  });
});
