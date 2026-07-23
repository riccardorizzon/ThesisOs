import { describe, expect, it, vi, afterEach, beforeEach } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { ProposalBundleModal } from "./ProposalBundleModal";
import { projectStorageKey } from "@/lib/projectScope";

const PROPOSALS_STORAGE_KEY = projectStorageKey("proposals");

afterEach(() => {
  cleanup();
  localStorage.clear();
});

describe("ProposalBundleModal", () => {
  beforeEach(() => {
    localStorage.setItem(
      PROPOSALS_STORAGE_KEY,
      JSON.stringify([
        {
          id: "p1",
          title: "Aggiornamento proposto: glossario STIGMATA",
          summary: "Definizione operativa del termine",
        },
        {
          id: "p2",
          title: "Modifica paragrafo §3.2",
        },
      ])
    );
  });

  it("lists pending proposals with Italian copy", () => {
    render(
      <ProposalBundleModal open onClose={vi.fn()} />
    );

    expect(screen.getByText(/Chiudi sessione/i)).toBeInTheDocument();
    expect(screen.getByText(/2 modifiche in sospeso/i)).toBeInTheDocument();
    expect(
      screen.getByText("Aggiornamento proposto: glossario STIGMATA")
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Accetta o rifiuta tutte le proposte insieme/i)
    ).toBeInTheDocument();
  });

  it("atomic approve clears all proposals", () => {
    const onResolved = vi.fn();
    render(
      <ProposalBundleModal open onClose={vi.fn()} onResolved={onResolved} />
    );

    fireEvent.click(screen.getByTestId("approve-all-proposals"));

    expect(onResolved).toHaveBeenCalledWith(
      "approve",
      expect.arrayContaining([
        expect.objectContaining({ id: "p1" }),
        expect.objectContaining({ id: "p2" }),
      ])
    );
    expect(localStorage.getItem(PROPOSALS_STORAGE_KEY)).toBe("[]");
  });

  it("atomic reject clears all proposals", () => {
    const onResolved = vi.fn();
    render(
      <ProposalBundleModal open onClose={vi.fn()} onResolved={onResolved} />
    );

    fireEvent.click(screen.getByTestId("reject-all-proposals"));

    expect(onResolved).toHaveBeenCalledWith("reject", expect.any(Array));
    expect(localStorage.getItem(PROPOSALS_STORAGE_KEY)).toBe("[]");
  });

  it("shows empty state when no proposals", () => {
    localStorage.setItem(PROPOSALS_STORAGE_KEY, "[]");
    render(
      <ProposalBundleModal open onClose={vi.fn()} />
    );

    expect(
      screen.getByText(/Nessuna proposta in sospeso/i)
    ).toBeInTheDocument();
  });
});
