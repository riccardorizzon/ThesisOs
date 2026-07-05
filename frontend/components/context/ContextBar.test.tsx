import { describe, expect, it, afterEach, vi } from "vitest";
import { fireEvent, render, screen, cleanup } from "@testing-library/react";
import { ContextBar } from "@/components/context/ContextBar";
import { ConstraintChip } from "@/components/context/ConstraintChip";
import { DecisionBadge } from "@/components/context/DecisionBadge";
import {
  CONTEXT_OPEN_CONTESTO_EVENT,
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
  it("matches Spec §6.4 pattern with voci ordering", () => {
    expect(formatContextBarLabel(contextBarCounts(CONTEXT_STUB))).toBe(
      "0 fonti · 2 decisioni · 0 voci · 0 citazioni"
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
  it("renders live counts and project phase when unscoped", () => {
    render(<ContextBar packet={CONTEXT_STUB} />);
    expect(
      screen.getByText("0 fonti · 2 decisioni · 0 voci · 0 citazioni")
    ).toBeInTheDocument();
    expect(screen.getByTestId("context-scope-chip")).toHaveTextContent(
      "Sviluppo argomentativo"
    );
  });

  it("shows entity title in scope chip when scoped", () => {
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
        selectionAnchor="§2.1"
      />
    );
    expect(screen.getByTestId("context-scope-chip")).toHaveTextContent(
      "Cap. 2 — Quadro teorico · §2.1"
    );
  });

  it("shows skeleton while loading", () => {
    render(<ContextBar loading />);
    expect(screen.getByTestId("context-bar-skeleton")).toBeInTheDocument();
    expect(screen.queryByTestId("context-bar-content")).not.toBeInTheDocument();
  });

  it("calls onScopeClick when scope chip clicked", () => {
    const onScopeClick = vi.fn();
    render(<ContextBar packet={CONTEXT_STUB} onScopeClick={onScopeClick} />);
    fireEvent.click(screen.getByTestId("context-scope-chip"));
    expect(onScopeClick).toHaveBeenCalledOnce();
  });

  it("calls onOpenContestoTab and emits custom event when counts clicked", () => {
    const onOpenContestoTab = vi.fn();
    const listener = vi.fn();
    window.addEventListener(CONTEXT_OPEN_CONTESTO_EVENT, listener);

    render(
      <ContextBar packet={CONTEXT_STUB} onOpenContestoTab={onOpenContestoTab} />
    );
    fireEvent.click(screen.getByTestId("context-summary"));
    expect(onOpenContestoTab).toHaveBeenCalledOnce();
    expect(listener).toHaveBeenCalledOnce();

    window.removeEventListener(CONTEXT_OPEN_CONTESTO_EVENT, listener);
  });

  it("applies warning styling when warningState active", () => {
    render(
      <ContextBar
        packet={CONTEXT_STUB}
        warningState={{ active: true, message: "Decisione vincolante attiva" }}
      />
    );
    expect(screen.getByTestId("context-bar")).toHaveClass("border-warning/30");
    expect(screen.getByTestId("context-bar-warning-message")).toHaveTextContent(
      "Decisione vincolante attiva"
    );
  });

  it("renders live counts from populated packet fields", () => {
    render(
      <ContextBar
        packet={{
          ...CONTEXT_STUB,
          relevant_sources: [{ id: "s1", title: "Benjamin" }],
          concepts: Array.from({ length: 18 }, (_, i) => ({
            id: `c${i}`,
            title: `Concetto ${i}`,
          })),
          decisions: Array.from({ length: 4 }, (_, i) => ({
            id: `d${i}`,
            summary: `Decision ${i}`,
            binding: true,
          })),
          citations_available: Array.from({ length: 34 }, (_, i) => ({
            id: `cit${i}`,
            label: `Cit ${i}`,
          })),
        }}
      />
    );
    expect(
      screen.getByText("1 fonti · 4 decisioni · 18 voci · 34 citazioni")
    ).toBeInTheDocument();
  });
});
