import { describe, expect, it } from "vitest";
import {
  computeProgressPct,
  findContinueTarget,
  progressPhaseLabel,
  STATUS_FACTOR,
} from "./progress";
import type { ProgressChapter } from "./progress";

describe("computeProgressPct", () => {
  it("returns 0 for empty chapters", () => {
    expect(computeProgressPct([])).toBe(0);
  });

  it("uses deterministic formula per ADR-0040", () => {
    const chapters: ProgressChapter[] = [
      { id: "1", title: "A", status: "draft", weight: 1 },
      { id: "2", title: "B", status: "approved", weight: 1 },
    ];
    const expected =
      ((1 * STATUS_FACTOR.draft + 1 * STATUS_FACTOR.approved) / 2) * 100;
    expect(computeProgressPct(chapters)).toBe(Math.round(expected));
  });

  it("respects chapter weights", () => {
    const chapters: ProgressChapter[] = [
      { id: "1", title: "A", status: "approved", weight: 2 },
      { id: "2", title: "B", status: "draft", weight: 1 },
    ];
    const num =
      2 * STATUS_FACTOR.approved + 1 * STATUS_FACTOR.draft;
    expect(computeProgressPct(chapters)).toBe(Math.round((num / 3) * 100));
  });

  it("matches fixed stub chapters snapshot", () => {
    const chapters: ProgressChapter[] = [
      { id: "1", status: "approved", title: "1", weight: 1 },
      { id: "2", status: "review", title: "2", weight: 1.2 },
      { id: "3", status: "draft", title: "3", weight: 1 },
      { id: "4", status: "draft", title: "4", weight: 1.5 },
      { id: "5", status: "draft", title: "5", weight: 1 },
    ];
    expect(computeProgressPct(chapters)).toBe(57);
  });
});

describe("findContinueTarget", () => {
  it("prefers draft or review chapter", () => {
    const chapters: ProgressChapter[] = [
      { id: "a", title: "Done", status: "approved" },
      { id: "b", title: "Working", status: "draft" },
    ];
    expect(findContinueTarget(chapters)).toEqual({
      href: "/writing/b",
      label: "Working",
    });
  });

  it("falls back to writing root when empty", () => {
    expect(findContinueTarget([])).toEqual({
      href: "/writing",
      label: "Inizia a scrivere",
    });
  });
});

describe("progressPhaseLabel", () => {
  it("returns phase strings for progress bands", () => {
    expect(progressPhaseLabel(0)).toBe("Progetto vuoto");
    expect(progressPhaseLabel(0, { fashionEmptyPhase: true })).toBe(
      "Prima dei dieci minuti"
    );
    expect(progressPhaseLabel(100)).toBe("Capitoli approvati");
  });

  it("keeps fashion empty copy only when opted in", () => {
    expect(progressPhaseLabel(0, { fashionEmptyPhase: true })).toBe(
      "Prima dei dieci minuti"
    );
  });
});
