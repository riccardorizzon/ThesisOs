import { describe, expect, it, vi, afterEach } from "vitest";
import {
  canCiteSource,
  dispatchInsertCitation,
  EXCLUDED_CITE_BLOCKED_MESSAGE,
  formatCitationMarker,
  INSERT_CITATION_EVENT,
} from "@/lib/citationInsert";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("formatCitationMarker", () => {
  it("formats [@AuthorYear] from subtitle and meta", () => {
    expect(
      formatCitationMarker({
        subtitle: "Walter Benjamin",
        meta: "1936 · Libro",
      })
    ).toBe("[@Benjamin1936]");
  });

  it("uses n.d. when year missing", () => {
    expect(formatCitationMarker({ subtitle: "John Doe" })).toBe("[@Doen.d.]");
  });
});

describe("canCiteSource", () => {
  it("allows approvata and candidata", () => {
    expect(canCiteSource("approvata")).toBe(true);
    expect(canCiteSource("candidata")).toBe(true);
  });

  it("blocks esclusa (IR-4)", () => {
    expect(canCiteSource("esclusa")).toBe(false);
  });
});

describe("dispatchInsertCitation", () => {
  it("dispatches thesisos:insert-citation with marker at cursor context", () => {
    const handler = vi.fn();
    window.addEventListener(INSERT_CITATION_EVENT, handler);

    dispatchInsertCitation({
      marker: "[@Benjamin1936]",
      sourceId: "benjamin-opera-arte",
      quote: "aura dell'opera d'arte",
    });

    expect(handler).toHaveBeenCalledTimes(1);
    const event = handler.mock.calls[0][0] as CustomEvent<{
      marker: string;
      sourceId: string;
      quote?: string;
    }>;
    expect(event.detail.marker).toBe("[@Benjamin1936]");
    expect(event.detail.sourceId).toBe("benjamin-opera-arte");
    expect(event.detail.quote).toBe("aura dell'opera d'arte");

    window.removeEventListener(INSERT_CITATION_EVENT, handler);
  });
});

describe("EXCLUDED_CITE_BLOCKED_MESSAGE", () => {
  it("is Italian operator copy", () => {
    expect(EXCLUDED_CITE_BLOCKED_MESSAGE).toContain("esclusa");
    expect(EXCLUDED_CITE_BLOCKED_MESSAGE).toContain("corpus");
  });
});
