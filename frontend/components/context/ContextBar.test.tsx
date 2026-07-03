import { describe, expect, it, afterEach } from "vitest";
import { render, screen, within, cleanup } from "@testing-library/react";
import { ContextBar } from "@/components/context/ContextBar";
import { ConstraintChip } from "@/components/context/ConstraintChip";
import { DecisionBadge } from "@/components/context/DecisionBadge";
import {
  CONTEXT_STUB,
  contextBarCounts,
  formatContextBarLabel,
} from "@/lib/contextClient";

afterEach(() => cleanup());

describe("contextBarCounts", () => {
  it("derives counts from packet fields", () => {
    expect(contextBarCounts(CONTEXT_STUB)).toEqual({
      sources: 0,
      concepts: 0,
      decisions: 2,
      citations: 0,
    });
  });
});

describe("formatContextBarLabel", () => {
  it("matches Spec §6.4 pattern", () => {
    expect(formatContextBarLabel(contextBarCounts(CONTEXT_STUB))).toBe(
      "0 fonti · 0 concetti · 2 decisioni · 0 citazioni"
    );
  });
});

describe("ConstraintChip", () => {
  it("renders corpus exclusion code and label", () => {
    render(
      <ConstraintChip constraint="CORPUS-02: Barthes Mythologies — escluso dal corpus attivo" />
    );
    expect(screen.getByTestId("constraint-chip-CORPUS-02")).toBeInTheDocument();
    expect(screen.getByText("CORPUS-02")).toBeInTheDocument();
    expect(
      screen.getByText("Barthes Mythologies — escluso dal corpus attivo")
    ).toBeInTheDocument();
  });
});

describe("DecisionBadge", () => {
  it("shows binding decision count", () => {
    render(<DecisionBadge decisions={CONTEXT_STUB.decisions} />);
    expect(screen.getByTestId("decision-badge")).toHaveTextContent(
      "2 decisioni vincolanti"
    );
  });

  it("renders nothing when no binding decisions", () => {
    const { container } = render(
      <DecisionBadge
        decisions={[{ id: "x", summary: "optional", binding: false }]}
      />
    );
    expect(container).toBeEmptyDOMElement();
  });
});

describe("ContextBar", () => {
  it("renders summary label and entity phase", () => {
    render(<ContextBar packet={CONTEXT_STUB} />);
    expect(
      screen.getByText("0 fonti · 0 concetti · 2 decisioni · 0 citazioni")
    ).toBeInTheDocument();
    expect(screen.getByText("Sviluppo argomentativo")).toBeInTheDocument();
  });

  it("shows entity title when scoped", () => {
    render(
      <ContextBar
        packet={{
          ...CONTEXT_STUB,
          entity: {
            type: "chapter",
            id: "2",
            title: "Cap. 2 — Quadro teorico",
          },
        }}
      />
    );
    expect(screen.getByText("Cap. 2 — Quadro teorico")).toBeInTheDocument();
  });

  it("renders corpus constraint chips from packet", () => {
    render(<ContextBar packet={CONTEXT_STUB} />);
    const indicators = screen.getByTestId("context-indicators");
    expect(
      within(indicators).getByTestId("constraint-chip-CORPUS-02")
    ).toBeInTheDocument();
    expect(
      within(indicators).getByTestId("constraint-chip-CORPUS-03")
    ).toBeInTheDocument();
  });

  it("renders decision badge for binding decisions", () => {
    render(<ContextBar packet={CONTEXT_STUB} />);
    const indicators = screen.getByTestId("context-indicators");
    expect(within(indicators).getByTestId("decision-badge")).toHaveTextContent(
      "2 decisioni vincolanti"
    );
  });
});
