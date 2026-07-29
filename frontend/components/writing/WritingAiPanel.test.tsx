import { describe, expect, it, vi, afterEach, beforeEach } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { WritingAiPanel } from "./WritingAiPanel";
import { FIXTURE_CONTEXT_PACKET } from "@/lib/fixtures/contextFixture";
import {
  _resetProposalQueueForTests,
  getPendingProposalCount,
} from "@/lib/proposalQueue";
import * as aiActions from "@/lib/aiActions";
import { validateProjectCitations } from "@/lib/citationClient";

vi.mock("@/lib/citationClient", () => ({
  validateProjectCitations: vi.fn(),
}));

const mockedValidateCitations = vi.mocked(validateProjectCitations);

afterEach(() => {
  cleanup();
  _resetProposalQueueForTests();
  vi.restoreAllMocks();
});

beforeEach(() => {
  _resetProposalQueueForTests();
  mockedValidateCitations.mockResolvedValue({ issues: [], blocking: false });
});

describe("WritingAiPanel", () => {
  it("renders disabled AI action buttons without context packet", () => {
    render(<WritingAiPanel />);

    expect(screen.getByTestId("writing-ai-panel")).toBeTruthy();
    const rewrite = screen.getByRole("button", { name: /Riscrivi/i });
    expect(rewrite).toBeDisabled();
    expect(rewrite).toHaveAttribute("title", "Contesto non disponibile");
  });

  it("disables selection-only actions when selection is empty", () => {
    render(
      <WritingAiPanel
        contextPacket={FIXTURE_CONTEXT_PACKET}
        chapterContent="Contenuto del capitolo."
      />
    );

    const rewrite = screen.getByRole("button", { name: /Riscrivi/i });
    expect(rewrite).toBeDisabled();
    expect(rewrite).toHaveAttribute("title", "Seleziona un passaggio nel capitolo");

    const verify = screen.getByRole("button", { name: /Verifica/i });
    expect(verify).not.toBeDisabled();
  });

  it("streams action output and adds proposal on Applica without mutating chapter", async () => {
    vi.spyOn(aiActions, "streamWritingAction").mockImplementation(async (_params, onEvent) => {
      onEvent({ event: "token", data: { text: "Testo " } });
      onEvent({ event: "token", data: { text: "proposta." } });
      onEvent({ event: "done", data: { draft: "Testo proposta." } });
    });

    render(
      <WritingAiPanel
        chapterId="3"
        contextPacket={FIXTURE_CONTEXT_PACKET}
        selectionText="Passaggio di prova"
        chapterContent="Capitolo intero"
      />
    );

    fireEvent.click(screen.getByRole("button", { name: /Riscrivi/i }));

    await waitFor(() => {
      expect(screen.getByTestId("ai-stream-output")).toHaveTextContent("Testo proposta.");
    });

    fireEvent.click(screen.getByTestId("applica-button"));
    expect(screen.getByTestId("ai-anteprima")).toBeTruthy();

    fireEvent.click(screen.getByTestId("confirm-proposal"));

    await waitFor(() => {
      expect(getPendingProposalCount()).toBe(1);
    });
    expect(screen.queryByTestId("ai-stream-output")).toBeNull();
  });

  it("shows API error instead of mock stream when LLM unavailable", async () => {
    vi.spyOn(aiActions, "streamWritingAction").mockImplementation(async (_params, onEvent) => {
      onEvent({
        event: "error",
        data: { code: "llm_not_configured", message: "LLM runtime not configured" },
      });
    });

    render(
      <WritingAiPanel
        contextPacket={FIXTURE_CONTEXT_PACKET}
        selectionText="Selezione"
        chapterContent="Capitolo"
      />
    );

    fireEvent.click(screen.getByRole("button", { name: /Verifica/i }));

    await waitFor(() => {
      expect(screen.getByTestId("ai-stream-output")).toHaveTextContent(
        "LLM runtime not configured"
      );
    });
  });

  it("discards partial stream on cancel", async () => {
    let rejectStream: (() => void) | undefined;
    vi.spyOn(aiActions, "streamWritingAction").mockImplementation(
      (_params, onEvent, signal) =>
        new Promise<void>((resolve) => {
          onEvent({ event: "token", data: { text: "Parziale" } });
          signal?.addEventListener("abort", () => resolve());
          rejectStream = () => {
            resolve();
          };
        })
    );

    render(
      <WritingAiPanel
        contextPacket={FIXTURE_CONTEXT_PACKET}
        selectionText="Selezione"
        chapterContent="Capitolo"
      />
    );

    fireEvent.click(screen.getByRole("button", { name: /Espandi/i }));

    await waitFor(() => {
      expect(screen.getByTestId("ai-stream-output")).toHaveTextContent("Parziale");
    });

    expect(screen.getByText("Generazione in corso…")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Interrompi/i }));
    rejectStream?.();

    await waitFor(() => {
      expect(screen.queryByTestId("ai-stream-output")).toBeNull();
    });
    expect(getPendingProposalCount()).toBe(0);
  });

  it("blocks applying AI output with an unlinked author-date citation", async () => {
    vi.spyOn(aiActions, "streamWritingAction").mockImplementation(
      async (_params, onEvent) => {
        onEvent({
          event: "done",
          data: { draft: "Affermazione (FantomaAutore, 2050)." },
        });
      }
    );
    mockedValidateCitations.mockResolvedValue({
      blocking: true,
      issues: [
        {
          start: 13,
          end: 38,
          code: "unlinked_author_date",
          message: "Citazione non collegata alla bibliografia del progetto",
          suggestion: "Aggiungi o collega questa fonte alla bibliografia",
          matched: "(FantomaAutore, 2050)",
        },
      ],
    });
    render(
      <WritingAiPanel
        contextPacket={FIXTURE_CONTEXT_PACKET}
        chapterContent="Capitolo"
      />
    );

    fireEvent.click(screen.getByRole("button", { name: /Verifica/i }));

    expect(
      await screen.findByText(/FantomaAutore, 2050/)
    ).toBeInTheDocument();
    expect(screen.getByTestId("applica-button")).toBeDisabled();
    fireEvent.click(screen.getByTestId("applica-override-button"));
    expect(screen.getByTestId("applica-button")).toBeEnabled();
  });

  it("keeps Applica disabled while project citation validation is pending", async () => {
    vi.spyOn(aiActions, "streamWritingAction").mockImplementation(
      async (_params, onEvent) => {
        onEvent({ event: "done", data: { draft: "Testo (Benjamin, 1936)." } });
      }
    );
    mockedValidateCitations.mockImplementation(
      () => new Promise(() => undefined)
    );
    render(
      <WritingAiPanel
        contextPacket={FIXTURE_CONTEXT_PACKET}
        chapterContent="Capitolo"
      />
    );

    fireEvent.click(screen.getByRole("button", { name: /Verifica/i }));

    expect(
      await screen.findByText("Verifica citazioni in corso…")
    ).toBeInTheDocument();
    expect(screen.getByTestId("applica-button")).toBeDisabled();
    expect(
      screen.queryByTestId("applica-override-button")
    ).not.toBeInTheDocument();
  });

  it("fails closed when project citation validation is unavailable", async () => {
    vi.spyOn(aiActions, "streamWritingAction").mockImplementation(
      async (_params, onEvent) => {
        onEvent({ event: "done", data: { draft: "Testo (Benjamin, 1936)." } });
      }
    );
    mockedValidateCitations.mockRejectedValue(
      new Error("Verifica citazioni non disponibile. Riprova.")
    );
    render(
      <WritingAiPanel
        contextPacket={FIXTURE_CONTEXT_PACKET}
        chapterContent="Capitolo"
      />
    );

    fireEvent.click(screen.getByRole("button", { name: /Verifica/i }));

    expect(
      await screen.findByText("Verifica citazioni non disponibile. Riprova.")
    ).toBeInTheDocument();
    expect(screen.getByTestId("applica-button")).toBeDisabled();
    expect(screen.getByTestId("applica-override-button")).toBeInTheDocument();
  });

  it("renders loop step events for verify and find-sources", async () => {
    vi.spyOn(aiActions, "streamWritingAction").mockImplementation(async (_params, onEvent) => {
      onEvent({
        event: "step",
        data: { phase: "retrieval", label: "Ricerca nel corpus", detail: "artigianato" },
      });
      onEvent({ event: "token", data: { text: "Risposta." } });
      onEvent({ event: "done", data: { draft: "Risposta.", meta: { search_count: 1, chunk_count: 2 } } });
    });

    render(
      <WritingAiPanel
        contextPacket={FIXTURE_CONTEXT_PACKET}
        chapterContent="Capitolo"
      />
    );

    fireEvent.click(screen.getByRole("button", { name: /Verifica/i }));

    await waitFor(() => {
      expect(screen.getByTestId("ai-loop-steps")).toBeInTheDocument();
    });
    expect(screen.getByTestId("ai-loop-steps")).toHaveTextContent("Ricerca nel corpus");
    expect(screen.getByTestId("ai-loop-steps")).toHaveTextContent("artigianato");
  });

  it("does not render loop steps for rewrite actions", async () => {
    vi.spyOn(aiActions, "streamWritingAction").mockImplementation(async (_params, onEvent) => {
      onEvent({
        event: "step",
        data: { phase: "retrieval", label: "Ricerca nel corpus", detail: "artigianato" },
      });
      onEvent({ event: "done", data: { draft: "Riscritto." } });
    });

    render(
      <WritingAiPanel
        contextPacket={FIXTURE_CONTEXT_PACKET}
        selectionText="Passaggio"
        chapterContent="Capitolo"
      />
    );

    fireEvent.click(screen.getByRole("button", { name: /Riscrivi/i }));

    await waitFor(() => {
      expect(screen.getByTestId("ai-stream-output")).toHaveTextContent("Riscritto.");
    });
    expect(screen.queryByTestId("ai-loop-steps")).toBeNull();
  });
});
