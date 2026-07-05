"use client";

import { useEffect, useRef } from "react";
import { postChatStream } from "@/lib/api";
import { ConversationList } from "@/components/ConversationList";
import { InputBox } from "@/components/InputBox";
import { MessageBubble } from "@/components/MessageBubble";
import { useChatStore } from "@/lib/store";

/**
 * AI power mode chat — relocated from /chat to /ai (ADR-0036).
 * Layer: Business (Product Plane)
 */
export function AiChatView() {
  const {
    conversationId,
    messages,
    streaming,
    error,
    setConversationId,
    addMessage,
    appendToLastAssistant,
    setStreaming,
    setError,
  } = useChatStore();
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => () => abortRef.current?.abort(), []);

  async function send(text: string) {
    abortRef.current?.abort();
    const ac = new AbortController();
    abortRef.current = ac;
    setError(null);
    addMessage({ role: "user", content: text });
    addMessage({ role: "assistant", content: "" });
    setStreaming(true);
    try {
      await postChatStream(
        { message: text, conversation_id: conversationId ?? undefined },
        (e) => {
          if (e.event === "token") appendToLastAssistant(e.data.text);
          else if (e.event === "done") setConversationId(e.data.conversation_id);
          else if (e.event === "error") setError(e.data.message);
        },
        ac.signal
      );
    } catch (err) {
      if (!(err instanceof DOMException && err.name === "AbortError")) {
        setError(String(err));
      }
    } finally {
      setStreaming(false);
    }
  }

  return (
    <div className="flex h-[calc(100vh-3rem)]">
      <ConversationList activeId={conversationId} />
      <section className="flex flex-1 flex-col">
        <header className="border-b border-border px-4 py-3">
          <h1 className="text-sm font-semibold text-ink">AI — modalità avanzata</h1>
          <p className="text-xs text-ink-muted">
            Chat libera con runtime qualificato. Le azioni contestuali vivono nei moduli.
          </p>
        </header>
        <div className="flex-1 space-y-3 overflow-y-auto p-4">
          {messages.map((m, i) => (
            <MessageBubble key={i} message={m} />
          ))}
          {error && (
            <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </div>
          )}
        </div>
        <InputBox disabled={streaming} onSend={send} />
      </section>
    </div>
  );
}
