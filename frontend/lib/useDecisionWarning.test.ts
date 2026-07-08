import { describe, expect, it } from "vitest";
import { renderHook } from "@testing-library/react";
import { FIXTURE_CONTEXT_PACKET } from "@/lib/fixtures/contextFixture";
import { parseDecision } from "@/lib/decisionClient";
import {
  computeDecisionWarning,
  useDecisionWarning,
} from "@/lib/useDecisionWarning";

describe("computeDecisionWarning", () => {
  it("returns inactive when no binding conflict", () => {
    const result = computeDecisionWarning({ packet: FIXTURE_CONTEXT_PACKET });
    expect(result).toEqual({ active: false, message: null });
  });

  it("activates when entity chapter matches influenced chapters and selection overlaps", () => {
    const decision = parseDecision({
      id: "dec-012",
      title: "DEC-012",
      summary:
        "Benjamin: aura vs riproducibilità. Influenza: Cap. 2, Cap. 3",
      binding: true,
    });

    const packet = {
      ...FIXTURE_CONTEXT_PACKET,
      decisions: [
        {
          id: decision.id,
          title: decision.displayId,
          summary: decision.summary,
          binding: true,
        },
      ],
      entity: {
        type: "chapter",
        id: "2",
        title: "Cap. 2 — Quadro teorico",
      },
    };

    const result = computeDecisionWarning({
      packet,
      selectionText: "Benjamin e l'aura nell'opera d'arte",
    });

    expect(result.active).toBe(true);
    expect(result.message).toBe("Attenzione: decisione vincolante");
    expect(result.decisionId).toBe("dec-012");
  });

  it("stays inactive when chapter matches but selection does not overlap", () => {
    const packet = {
      ...FIXTURE_CONTEXT_PACKET,
      decisions: [
        {
          id: "dec-012",
          title: "DEC-012",
          summary: "Benjamin: aura vs riproducibilità. Influenza: Cap. 2",
          binding: true,
        },
      ],
      entity: {
        type: "chapter",
        id: "2",
        title: "Cap. 2 — Quadro teorico",
      },
    };

    const result = computeDecisionWarning({
      packet,
      selectionText: "Testo neutro senza overlap",
    });

    expect(result.active).toBe(false);
  });
});

describe("useDecisionWarning", () => {
  it("memoizes warning state from packet input", () => {
    const { result, rerender } = renderHook(
      ({ packet }) => useDecisionWarning({ packet }),
      { initialProps: { packet: FIXTURE_CONTEXT_PACKET } }
    );

    expect(result.current.active).toBe(false);

    rerender({
      packet: {
        ...FIXTURE_CONTEXT_PACKET,
        entity: {
          type: "chapter",
          id: "2",
          title: "Cap. 2 — Quadro teorico",
        },
        decisions: [
          {
            id: "dec-012",
            title: "DEC-012",
            summary: "Benjamin: aura vs riproducibilità. Influenza: Cap. 2",
            binding: true,
          },
        ],
      },
    });

    expect(result.current.active).toBe(false);
  });
});
