import { describe, expect, it, beforeEach, afterEach } from "vitest";

import {
  PROPOSALS_STORAGE_KEY,
  SESSION_STATE_STORAGE_KEY,
  formatSessionDuration,
  getPendingProposalCount,
  loadSessionState,
  parseWritingUrlState,
  readPendingProposals,
  resolveProposalBundle,
  saveSessionState,
  serializeWritingUrlState,
} from "./sessionState";

describe("parseWritingUrlState", () => {
  it("parses section, source, and panel params", () => {
    expect(
      parseWritingUrlState("?section=3.2&source=src-benjamin&panel=fonte")
    ).toEqual({
      section: "3.2",
      source: "src-benjamin",
      panel: "fonte",
    });
  });

  it("ignores invalid panel values", () => {
    expect(parseWritingUrlState("panel=invalid")).toEqual({});
  });

  it("returns empty object for empty search", () => {
    expect(parseWritingUrlState("")).toEqual({});
  });
});

describe("serializeWritingUrlState", () => {
  it("builds writing path with query params", () => {
    expect(
      serializeWritingUrlState("cap-03", {
        section: "3.2",
        source: "src-benjamin-1936",
        panel: "fonte",
      })
    ).toBe(
      "/writing/cap-03?section=3.2&source=src-benjamin-1936&panel=fonte"
    );
  });

  it("appends section hash anchor when requested", () => {
    expect(
      serializeWritingUrlState(
        "cap-03",
        { section: "3.2" },
        { scrollAnchor: "section-3-2" }
      )
    ).toBe("/writing/cap-03?section=3.2#section-3-2");
  });
});

describe("session localStorage persistence", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  it("saves and loads session state", () => {
    saveSessionState({
      chapterId: "3",
      chapterTitle: "Cap. 3 — Metodologia",
      section: "3.2",
      panel: "fonte",
      scrollY: 420,
    });
    const loaded = loadSessionState();
    expect(loaded?.chapterId).toBe("3");
    expect(loaded?.section).toBe("3.2");
    expect(loaded?.panel).toBe("fonte");
    expect(loaded?.scrollY).toBe(420);
    expect(loaded?.startedAt).toBeTruthy();
  });

  it("tracks pending proposals from storage key", () => {
    localStorage.setItem(
      PROPOSALS_STORAGE_KEY,
      JSON.stringify([
        { id: "p1", title: "Proposta A" },
        { id: "p2", title: "Proposta B" },
      ])
    );
    expect(getPendingProposalCount()).toBe(2);
    expect(readPendingProposals()).toHaveLength(2);
  });

  it("resolveProposalBundle clears queue atomically", () => {
    localStorage.setItem(
      PROPOSALS_STORAGE_KEY,
      JSON.stringify([{ id: "p1", title: "Proposta A" }])
    );
    const resolved = resolveProposalBundle("approve");
    expect(resolved).toHaveLength(1);
    expect(getPendingProposalCount()).toBe(0);
  });
});

describe("formatSessionDuration", () => {
  it("formats hours and minutes", () => {
    const now = new Date("2026-07-04T14:14:00Z");
    const started = "2026-07-04T12:00:00Z";
    expect(formatSessionDuration(started, now)).toBe("2h 14m");
  });

  it("formats minutes only under one hour", () => {
    const now = new Date("2026-07-04T12:45:00Z");
    const started = "2026-07-04T12:00:00Z";
    expect(formatSessionDuration(started, now)).toBe("45m");
  });
});
