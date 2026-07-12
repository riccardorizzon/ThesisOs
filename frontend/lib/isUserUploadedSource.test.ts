import { describe, expect, it } from "vitest";

import { isUserUploadedSource } from "./isUserUploadedSource";
import type { SourceListItem } from "./sourcesTypes";

function source(overrides: Partial<SourceListItem> = {}): SourceListItem {
  return {
    id: "benjamin-opera-arte",
    slug: "benjamin-opera-arte",
    type: "source",
    title: "Benjamin",
    confidence: "non_valutata",
    knowledge_state: "linked",
    linked_counts: {
      sources: 0,
      chapters: 0,
      concepts: 0,
      decisions: 0,
      authors: 0,
      citations: 0,
    },
    created_by: "importazione",
    proposal_state: "nessuna",
    is_core: false,
    related_concepts: [],
    ...overrides,
  };
}

describe("isUserUploadedSource", () => {
  it("returns true when deletable flag is set", () => {
    expect(isUserUploadedSource(source({ deletable: true }))).toBe(true);
  });

  it("returns true for uploaded summary prefix", () => {
    expect(
      isUserUploadedSource(
        source({
          slug: "a35ea976-d245-4dc8-a63b-46afeb440364",
          summary: "Caricato · PDF",
        })
      )
    ).toBe(true);
  });

  it("returns false for seed catalog sources", () => {
    expect(
      isUserUploadedSource(
        source({ summary: "1936 · Fonte bibliografica", corpus_status: "approvata" })
      )
    ).toBe(false);
  });
});
