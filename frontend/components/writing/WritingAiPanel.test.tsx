import { describe, expect, it, vi, afterEach, beforeEach } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { WritingAiPanel } from "./WritingAiPanel";
import { CONTEXT_STUB } from "@/lib/contextClient";
import {
  _resetProposalQueueForTests,
  getPendingProposalCount,
} from "@/lib/proposalQueue";
import * as aiActions from "@/lib/aiActions";

afterEach(() => {
  cleanup();
  _resetProposalQueueForTests();
  vi.restoreAllMocks();
});

beforeEach(() => {
  _resetProposalQueueForTests();
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
        contextPacket={CONTEXT_STUB}
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
        contextPacket={CONTEXT_STUB}
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
        contextPacket={CONTEXT_STUB}
        selectionText="Selezione"
        chapterContent="Capitolo"
      />
    );

    fireEvent.click(screen.getByRole("button", { name: /Espandi/i }));

    await waitFor(() => {
      expect(screen.getByTestId("ai-stream-output")).toHaveTextContent("Parziale");
    });

    fireEvent.click(screen.getByRole("button", { name: /Annulla/i }));
    rejectStream?.();

    await waitFor(() => {
      expect(screen.queryByTestId("ai-stream-output")).toBeNull();
    });
    expect(getPendingProposalCount()).toBe(0);
  });
});
