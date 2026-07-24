import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { KnowledgeNotesPanel } from "@/components/knowledge/notes/KnowledgeNotesPanel";
import { memoryClient, type Memory } from "@/lib/memoryClient";

vi.mock("@/lib/memoryClient", async () => {
  const actual = await vi.importActual<typeof import("@/lib/memoryClient")>(
    "@/lib/memoryClient"
  );
  return {
    ...actual,
    memoryClient: {
      list: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
      delete: vi.fn(),
      listVersions: vi.fn(),
    },
  };
});

const note: Memory = {
  id: "note-1",
  kind: "note",
  title: "Nota metodologica",
  content: "Contenuto iniziale",
  metadata: {},
  key: null,
  pinned: false,
  source: "user",
  version: 1,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

beforeEach(() => {
  vi.mocked(memoryClient.list).mockResolvedValue([]);
  vi.mocked(memoryClient.create).mockResolvedValue(note);
  vi.mocked(memoryClient.update).mockResolvedValue({
    ...note,
    title: "Nota aggiornata",
    version: 2,
  });
  vi.mocked(memoryClient.delete).mockResolvedValue(undefined);
  vi.mocked(memoryClient.listVersions).mockResolvedValue([
    {
      memory_id: note.id,
      version: 1,
      title: note.title,
      content: note.content,
      metadata: {},
      source: "user",
      changed_at: note.updated_at,
    },
  ]);
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("KnowledgeNotesPanel", () => {
  it("creates a project-scoped note from the empty state", async () => {
    render(<KnowledgeNotesPanel />);
    expect(await screen.findByText("Nessuna nota ancora")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Nuova nota" }));
    fireEvent.change(screen.getByLabelText("Titolo nota"), {
      target: { value: "Nota metodologica" },
    });
    fireEvent.change(screen.getByLabelText("Contenuto nota"), {
      target: { value: "Contenuto iniziale" },
    });
    fireEvent.click(screen.getByLabelText("Includi nel contesto AI"));
    fireEvent.click(screen.getByRole("button", { name: "Salva nota" }));

    await waitFor(() => {
      expect(memoryClient.create).toHaveBeenCalledWith({
        kind: "note",
        title: "Nota metodologica",
        content: "Contenuto iniziale",
        pinned: true,
      });
    });
    expect(screen.getByText("Nota metodologica")).toBeInTheDocument();
  });

  it("edits, versions, and deletes an existing note", async () => {
    vi.mocked(memoryClient.list).mockResolvedValue([note]);
    render(<KnowledgeNotesPanel />);

    fireEvent.click(await screen.findByRole("button", { name: "Nota metodologica" }));
    expect(memoryClient.listVersions).toHaveBeenCalledWith("note-1");
    expect(await screen.findByText("Versione 1")).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Titolo nota"), {
      target: { value: "Nota aggiornata" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Salva modifiche" }));
    await waitFor(() => {
      expect(memoryClient.update).toHaveBeenCalledWith(
        "note-1",
        expect.objectContaining({
          title: "Nota aggiornata",
          expected_version: 1,
        })
      );
    });

    fireEvent.click(screen.getByRole("button", { name: "Elimina nota" }));
    fireEvent.click(
      screen.getByRole("button", { name: "Conferma eliminazione nota" })
    );
    await waitFor(() => {
      expect(memoryClient.delete).toHaveBeenCalledWith("note-1");
    });
  });
});
