import { describe, expect, it, afterEach } from "vitest";
import { render, screen, within, cleanup } from "@testing-library/react";
import { ContextInspector } from "@/components/context/ContextInspector";
import { CONTEXT_STUB } from "@/lib/contextClient";

afterEach(() => cleanup());

describe("ContextInspector", () => {
  it("renders accordion sections without decision cards", () => {
    render(<ContextInspector packet={CONTEXT_STUB} />);
    expect(screen.getByTestId("context-inspector")).toBeInTheDocument();
    expect(screen.getByTestId("inspector-ambito")).toBeInTheDocument();
    expect(screen.getByTestId("inspector-vincoli")).toBeInTheDocument();
    expect(screen.getByTestId("inspector-definizioni")).toBeInTheDocument();
    expect(screen.getByTestId("inspector-fonti")).toBeInTheDocument();
    expect(screen.getByTestId("inspector-regole")).toBeInTheDocument();
    expect(screen.queryByTestId("inspector-decisioni")).not.toBeInTheDocument();
  });

  it("shows human-readable scope and corpus constraints", () => {
    render(
      <ContextInspector
        packet={{
          ...CONTEXT_STUB,
          entity: {
            type: "chapter",
            id: "3",
            title: "Cap. 3 — Metodologia",
            snippet: "Sezione introduttiva al metodo.",
          },
        }}
        selectionAnchor="§3.2"
      />
    );
    expect(
      screen.getByText("Cap. 3 — Metodologia · §3.2")
    ).toBeInTheDocument();
    expect(
      screen.getByText("CORPUS-02: Barthes Mythologies — escluso dal corpus attivo")
    ).toBeInTheDocument();
  });

  it("shows empty states when sections have no content", () => {
    render(
      <ContextInspector
        packet={{
          ...CONTEXT_STUB,
          corpus_constraints: [],
          definitions: [],
          relevant_sources: [],
          writing_rules: [],
        }}
      />
    );
    expect(
      within(screen.getByTestId("inspector-vincoli")).getByText(
        "Nessun vincolo corpus attivo."
      )
    ).toBeInTheDocument();
    expect(
      within(screen.getByTestId("inspector-definizioni")).getByText(
        "Nessuna definizione nel contesto attuale."
      )
    ).toBeInTheDocument();
    expect(
      within(screen.getByTestId("inspector-fonti")).getByText(
        "Nessuna fonte nel contesto attuale."
      )
    ).toBeInTheDocument();
    expect(
      within(screen.getByTestId("inspector-regole")).getByText(
        "Nessuna regola di scrittura nel contesto attuale."
      )
    ).toBeInTheDocument();
  });

  it("lists definitions, sources, and writing rules when present", () => {
    render(
      <ContextInspector
        packet={{
          ...CONTEXT_STUB,
          definitions: [{ term: "Aura", definition: "Unicità dell'opera d'arte." }],
          relevant_sources: [{ id: "src-1", title: "Benjamin (1936)" }],
          writing_rules: ["Italiano accademico"],
        }}
      />
    );
    expect(screen.getByText("Aura")).toBeInTheDocument();
    expect(screen.getByText("Unicità dell'opera d'arte.")).toBeInTheDocument();
    expect(screen.getByText("Benjamin (1936)")).toBeInTheDocument();
    expect(screen.getByText("Italiano accademico")).toBeInTheDocument();
  });
});
