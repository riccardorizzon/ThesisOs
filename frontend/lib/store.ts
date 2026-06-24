import { create } from "zustand";

export type ChatMessage = { role: "user" | "assistant"; content: string };

type ChatState = {
  conversationId: string | null;
  messages: ChatMessage[];
  streaming: boolean;
  error: string | null;
  setConversationId: (id: string | null) => void;
  addMessage: (m: ChatMessage) => void;
  appendToLastAssistant: (delta: string) => void;
  setStreaming: (v: boolean) => void;
  setError: (e: string | null) => void;
};

export const useChatStore = create<ChatState>((set) => ({
  conversationId: null,
  messages: [],
  streaming: false,
  error: null,
  setConversationId: (id) => set({ conversationId: id }),
  addMessage: (m) => set((s) => ({ messages: [...s.messages, m] })),
  appendToLastAssistant: (delta) =>
    set((s) => {
      const msgs = s.messages.slice();
      const last = msgs[msgs.length - 1];
      if (last && last.role === "assistant") msgs[msgs.length - 1] = { ...last, content: last.content + delta };
      return { messages: msgs };
    }),
  setStreaming: (v) => set({ streaming: v }),
  setError: (e) => set({ error: e }),
}));

// Preserve the existing UI route store
type UIState = { activeRoute: string; setActiveRoute: (r: string) => void };
export const useUIStore = create<UIState>((set) => ({
  activeRoute: "chat",
  setActiveRoute: (r) => set({ activeRoute: r }),
}));
