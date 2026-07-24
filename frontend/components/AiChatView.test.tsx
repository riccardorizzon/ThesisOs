import { render, screen, waitFor, cleanup, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";

import { AiChatView } from "@/components/AiChatView";

const mockReplace = vi.fn();
let searchParams = new URLSearchParams();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    replace: mockReplace,
    push: vi.fn(),
  }),
  useSearchParams: () => searchParams,
}));

vi.mock("@/lib/conversationClient", () => ({
  listConversations: vi.fn(),
  createConversation: vi.fn(),
  getConversationMessages: vi.fn(),
  renameConversation: vi.fn(),
  deleteConversation: vi.fn(),
}));

vi.mock("@/lib/api", () => ({
  postChatStream: vi.fn(),
}));

vi.mock("@/lib/companionClient", () => ({
  getCompanionResume: vi.fn(),
}));

import {
  createConversation,
  deleteConversation,
  getConversationMessages,
  listConversations,
  renameConversation,
} from "@/lib/conversationClient";
import { postChatStream } from "@/lib/api";
import { getCompanionResume } from "@/lib/companionClient";

const mockedList = vi.mocked(listConversations);
const mockedCreate = vi.mocked(createConversation);
const mockedDelete = vi.mocked(deleteConversation);
const mockedGetMessages = vi.mocked(getConversationMessages);
const mockedPostChat = vi.mocked(postChatStream);
const mockedGetCompanionResume = vi.mocked(getCompanionResume);
const mockedRename = vi.mocked(renameConversation);

const companionResume = {
  schema_version: "1",
  project_id: "thesis-agent",
  title: "Estetica e cultura visuale",
  author: "Ricky",
  institution: "Università",
  migration_run: null,
  progress_summary: "Il capitolo 3 è quasi completo.",
  continue_prompt: "Riprendiamo dal punto di ieri sul §3.6.",
  focus_chapter_id: "ch03",
  resume: {
    focus_chapter: "Capitolo 3",
    focus_section: "§3.6",
    focus_section_title: "Sintesi e costruzione di significato",
    focus_status: "in stesura",
    backlog: [],
    next_action: "Completa la sintesi finale.",
    session_notes: [],
    key_decisions: [],
    section_text: null,
    last_session_summary: null,
    work_artifact: null,
  },
};

beforeEach(() => {
  searchParams = new URLSearchParams();
  mockReplace.mockReset();
  mockedList.mockResolvedValue([]);
  mockedCreate.mockResolvedValue({
    id: "conv-new",
    project_id: "thesis-agent",
    title: null,
    created_at: "2026-07-07T12:00:00Z",
  });
  mockedGetMessages.mockResolvedValue([]);
  mockedRename.mockImplementation(async (id, title) => ({
    id,
    project_id: "thesis-agent",
    title,
    created_at: "2026-07-07T12:00:00Z",
  }));
  mockedDelete.mockResolvedValue(undefined);
  mockedPostChat.mockResolvedValue(undefined);
  mockedGetCompanionResume.mockResolvedValue(companionResume);
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("AiChatView", () => {
  it("loads persisted messages when conversation is in the URL", async () => {
    searchParams = new URLSearchParams("conversation=conv-1");
    mockedGetMessages.mockResolvedValue([
      {
        id: "m1",
        role: "user",
        content: "Ciao",
        created_at: "2026-07-07T12:00:00Z",
      },
      {
        id: "m2",
        role: "assistant",
        content: "Salve",
        created_at: "2026-07-07T12:00:01Z",
      },
    ]);

    render(<AiChatView />);

    await waitFor(() => {
      expect(mockedGetMessages).toHaveBeenCalledWith("conv-1");
    });
    expect(await screen.findByText("Ciao")).toBeInTheDocument();
    expect(screen.getByText("Salve")).toBeInTheDocument();
  });

  it("shows empty chat when no conversation is selected", async () => {
    render(<AiChatView />);

    await waitFor(() => {
      expect(mockedList).toHaveBeenCalled();
    });
    expect(mockedGetMessages).not.toHaveBeenCalled();
    expect(screen.getByTestId("ai-chat-view")).toBeInTheDocument();
  });

  it("shows the companion resume and sends the continuation marker only on action", async () => {
    render(<AiChatView />);

    expect(await screen.findByText("Estetica e cultura visuale")).toBeInTheDocument();
    expect(screen.getByText("§3.6")).toBeInTheDocument();
    expect(screen.getByText("in stesura")).toBeInTheDocument();
    expect(screen.getByText("Il capitolo 3 è quasi completo.")).toBeInTheDocument();
    expect(screen.getByText("Completa la sintesi finale.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Vai alla scrittura" })).toHaveAttribute(
      "href",
      "/writing",
    );
    expect(screen.getByRole("link", { name: "Vai alla revisione" })).toHaveAttribute(
      "href",
      "/review",
    );
    expect(screen.getByRole("link", { name: "Vai alle fonti" })).toHaveAttribute(
      "href",
      "/sources",
    );
    expect(mockedPostChat).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole("button", { name: "Continua da §3.6" }));

    await waitFor(() => {
      expect(mockedPostChat).toHaveBeenCalledWith(
        expect.objectContaining({ message: "__companion_open__" }),
        expect.any(Function),
        expect.any(AbortSignal),
      );
    });
    // The visible user text comes from the Resume packet (single source of
    // truth), not from a hardcoded string.
    expect(
      screen.getByText("Riprendiamo dal punto di ieri sul §3.6."),
    ).toBeInTheDocument();
  });

  it("uses the canonical home URL for conversation selection and stream completion", async () => {
    mockedList.mockResolvedValue([
      {
        id: "conv-a",
        project_id: "thesis-agent",
        title: "Tesi chat",
        created_at: "2026-07-07T12:00:00Z",
      },
    ]);
    mockedPostChat.mockImplementation(async (_body, onEvent) => {
      onEvent({
        event: "done",
        data: { conversation_id: "conv-new", message_id: "m1", usage: {} },
      });
    });
    render(<AiChatView />);

    fireEvent.click(await screen.findByTestId("conversation-item-conv-a"));
    expect(mockReplace).toHaveBeenCalledWith("/?conversation=conv-a");

    fireEvent.change(screen.getByPlaceholderText("Scrivi un messaggio…"), {
      target: { value: "Avvia" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Invia" }));
    await waitFor(() => {
      expect(mockReplace).toHaveBeenCalledWith("/?conversation=conv-new");
    });
  });

  it("replaces the assistant response and renders source metadata", async () => {
    mockedPostChat.mockImplementation(async (_body, onEvent) => {
      onEvent({ event: "token", data: { text: "Bozza da sostituire" } });
      onEvent({ event: "replace", data: { text: "Risposta verificata" } });
      onEvent({
        event: "sources",
        data: {
          sources: [
            {
              index: 1,
              chunk_id: "chunk-1",
              document_id: "doc-1",
              document_title: "The Craftsman",
              page_from: 42,
              score: 0.91,
            },
          ],
        },
      });
    });
    render(<AiChatView />);

    fireEvent.change(screen.getByPlaceholderText("Scrivi un messaggio…"), {
      target: { value: "Verifica questa idea" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Invia" }));

    expect(await screen.findByText("Risposta verificata")).toBeInTheDocument();
    expect(screen.queryByText("Bozza da sostituire")).not.toBeInTheDocument();
    expect(screen.getByText("The Craftsman")).toBeInTheDocument();
    expect(screen.getByText("p. 42")).toBeInTheDocument();
  });

  it("shows a stream error and removes the empty assistant placeholder", async () => {
    mockedPostChat.mockImplementation(async (_body, onEvent) => {
      onEvent({
        event: "error",
        data: {
          code: "request_failed",
          message: "Servizio non disponibile. Riprova.",
        },
      });
    });
    render(<AiChatView />);

    fireEvent.change(screen.getByPlaceholderText("Scrivi un messaggio…"), {
      target: { value: "Ciao" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Invia" }));

    expect(
      await screen.findByText("Servizio non disponibile. Riprova.")
    ).toBeInTheDocument();
    expect(screen.queryByText("…")).not.toBeInTheDocument();
  });

  it("exposes progress and cancels the active stream", async () => {
    let streamSignal: AbortSignal | undefined;
    mockedPostChat.mockImplementation(
      async (_body, _onEvent, signal) =>
        new Promise<void>((resolve) => {
          streamSignal = signal;
          signal?.addEventListener("abort", () => resolve(), { once: true });
        })
    );
    render(<AiChatView />);

    fireEvent.change(screen.getByPlaceholderText("Scrivi un messaggio…"), {
      target: { value: "Genera" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Invia" }));

    expect(await screen.findByText("Generazione in corso…")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Interrompi" }));

    expect(streamSignal?.aborted).toBe(true);
    await waitFor(() => {
      expect(
        screen.queryByRole("button", { name: "Interrompi" })
      ).not.toBeInTheDocument();
    });
    expect(screen.queryByText("…")).not.toBeInTheDocument();
  });
});

describe("ConversationList", () => {
  it("renders conversations from the API", async () => {
    searchParams = new URLSearchParams("conversation=conv-a");
    mockedList.mockResolvedValue([
      {
        id: "conv-a",
        project_id: "thesis-agent",
        title: "Tesi chat",
        created_at: "2026-07-07T12:00:00Z",
      },
      {
        id: "conv-b",
        project_id: "thesis-agent",
        title: "Revisione",
        created_at: "2026-07-07T11:00:00Z",
      },
    ]);

    render(<AiChatView />);

    expect(await screen.findByText("Tesi chat")).toBeInTheDocument();
    expect(screen.getByText("Revisione")).toBeInTheDocument();
    expect(screen.getByTestId("conversation-item-conv-a")).toHaveClass("font-medium");
  });

  it("renames a conversation from its action menu", async () => {
    mockedList.mockResolvedValue([
      {
        id: "conv-a",
        project_id: "thesis-agent",
        title: "New Conversation",
        created_at: "2026-07-07T12:00:00Z",
      },
    ]);
    render(<AiChatView />);

    fireEvent.click(
      await screen.findByRole("button", {
        name: /Azioni per la conversazione/,
      })
    );
    fireEvent.click(screen.getByRole("button", { name: "Rinomina" }));
    fireEvent.change(screen.getByLabelText("Nuovo titolo conversazione"), {
      target: { value: "Capitolo metodologico" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Salva titolo" }));

    await waitFor(() => {
      expect(mockedRename).toHaveBeenCalledWith(
        "conv-a",
        "Capitolo metodologico",
        "thesis-agent"
      );
    });
    expect(await screen.findByText("Capitolo metodologico")).toBeInTheDocument();
  });

  it("deletes the active conversation with confirmation and returns home", async () => {
    searchParams = new URLSearchParams("conversation=conv-a");
    mockedList.mockResolvedValue([
      {
        id: "conv-a",
        project_id: "thesis-agent",
        title: "Da eliminare",
        created_at: "2026-07-07T12:00:00Z",
      },
    ]);
    render(<AiChatView />);

    fireEvent.click(
      await screen.findByRole("button", {
        name: "Azioni per la conversazione Da eliminare",
      })
    );
    fireEvent.click(screen.getByRole("button", { name: "Elimina" }));
    fireEvent.click(
      screen.getByRole("button", { name: "Conferma eliminazione conversazione" })
    );

    await waitFor(() => {
      expect(mockedDelete).toHaveBeenCalledWith("conv-a", "thesis-agent");
    });
    expect(mockReplace).toHaveBeenCalledWith("/");
  });
});
