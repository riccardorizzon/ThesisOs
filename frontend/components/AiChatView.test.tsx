import { render, screen, waitFor, cleanup } from "@testing-library/react";
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
}));

vi.mock("@/lib/api", () => ({
  postChatStream: vi.fn(),
}));

import {
  createConversation,
  getConversationMessages,
  listConversations,
} from "@/lib/conversationClient";
import { postChatStream } from "@/lib/api";

const mockedList = vi.mocked(listConversations);
const mockedCreate = vi.mocked(createConversation);
const mockedGetMessages = vi.mocked(getConversationMessages);
const mockedPostChat = vi.mocked(postChatStream);

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
  mockedPostChat.mockResolvedValue(undefined);
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
});
