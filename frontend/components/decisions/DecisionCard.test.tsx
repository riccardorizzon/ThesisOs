import { describe, expect, it, vi, afterEach } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { DecisionCard } from "@/components/decisions/DecisionCard";
import {
  ASK_REVIEWER_EVENT,
  parseDecision,
  type DecisionView,
} from "@/lib/decisionClient";

afterEach(() => cleanup());

const bindingDecision: DecisionView = {
  id: "dec-012",
  displayId: "DEC-012",
  title: "Benjamin: aura vs riproducibilità",
  summary: "La riproducibilità tecnica non esaurisce l'aura benjaminiana.",
  fullSummary:
    "La riproducibilità tecnica non esaurisce l'aura benjaminiana. Influenza: Cap. 2, Cap. 3",
  binding: true,
  frozen: true,
  status: "vincolante",
  influencedChapters: ["Cap. 2", "Cap. 3"],
};

const openDecision: DecisionView = {
  id: "plat-01",
  displayId: "PLAT-01",
  title: "Migrazione ThesisOS",
  summary: "Comportamento agente in knowledge/thesis-agent/",
  fullSummary: "Comportamento agente in knowledge/thesis-agent/",
  binding: false,
  frozen: false,
  status: "aperta",
  influencedChapters: [],
};

describe("DecisionCard", () => {
  it("renders display id, binding badge, summary, and influenced chapters", () => {
    render(<DecisionCard decision={bindingDecision} />);

    expect(screen.getByText("DEC-012")).toBeInTheDocument();
    expect(screen.getByTestId("decision-status-badge")).toHaveTextContent(
      "Vincolante"
    );
    expect(
      screen.getByText("Benjamin: aura vs riproducibilità")
    ).toBeInTheDocument();
    expect(screen.getByText(/Influenza: Cap\. 2, Cap\. 3/)).toBeInTheDocument();
  });

  it("renders open decision badge", () => {
    render(<DecisionCard decision={openDecision} />);
    expect(screen.getByTestId("decision-status-badge")).toHaveTextContent(
      "Aperta"
    );
  });

  it("shows frozen read-only hint and blocked modal on edit attempt", () => {
    render(<DecisionCard decision={bindingDecision} />);

    expect(screen.getByTestId("frozen-readonly-hint")).toHaveTextContent(
      "Decisione vincolante — non modificabile"
    );

    fireEvent.click(screen.getByTestId("decision-frozen-edit-guard"));
    expect(screen.getByTestId("frozen-decision-modal")).toBeInTheDocument();
    expect(
      screen.getByRole("dialog").querySelector(".text-ink-muted")
    ).toHaveTextContent("Decisione vincolante — non modificabile");
  });

  it("expands full summary with Leggi", () => {
    render(<DecisionCard decision={bindingDecision} />);

    fireEvent.click(screen.getByRole("button", { name: "Leggi" }));
    expect(screen.getByTestId("decision-full-summary")).toHaveTextContent(
      "La riproducibilità tecnica non esaurisce l'aura benjaminiana."
    );
  });

  it("dispatches thesisos:ask-reviewer with decision id", () => {
    const handler = vi.fn();
    window.addEventListener(ASK_REVIEWER_EVENT, handler);

    render(<DecisionCard decision={bindingDecision} />);
    fireEvent.click(screen.getByTestId("ask-reviewer-button"));

    expect(handler).toHaveBeenCalledTimes(1);
    expect(
      (handler.mock.calls[0][0] as CustomEvent).detail
    ).toEqual({ decisionId: "dec-012" });

    window.removeEventListener(ASK_REVIEWER_EVENT, handler);
  });
});

describe("parseDecision", () => {
  it("derives display id from title when available", () => {
    const view = parseDecision({
      id: "stub-corpus-02",
      title: "CORPUS-02",
      summary: "Barthes Mythologies — escluso dal corpus attivo",
      binding: true,
    });
    expect(view.displayId).toBe("CORPUS-02");
    expect(view.status).toBe("vincolante");
    expect(view.frozen).toBe(true);
  });
});
