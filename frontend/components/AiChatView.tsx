"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { postChatStream } from "@/lib/api";
import { ConversationList } from "@/components/ConversationList";
import { InputBox } from "@/components/InputBox";
import { MessageBubble } from "@/components/MessageBubble";
import {
  getConversationMessages,
  type ConversationMessage,
} from "@/lib/conversationClient";
import { getActiveProjectId } from "@/lib/projectPrefs";
import type { ChatMessage } from "@/lib/store";

function toChatMessages(items: ConversationMessage[]): ChatMessage[] {
  return items
    .filter((m) => m.role === "user" || m.role === "assistant")
    .map((m) => ({
      role: m.role as "user" | "assistant",
      content: m.content,
    }));
}

/**
 * AI power mode chat — relocated from /chat to /ai (ADR-0036).
 * Layer: Business (Product Plane)
 */
export function AiChatView() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const conversationId = searchParams.get("conversation");

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [listRefresh, setListRefresh] = useState(0);
  const abortRef = useRef<AbortController | null>(null);

  const selectConversation = useCallback(
    (id: string) => {
      router.replace(`/ai?conversation=${encodeURIComponent(id)}`);
    },
    [router]
  );

  useEffect(() => () => abortRef.current?.abort(), []);

  useEffect(() => {
    if (!conversationId) {
      setMessages([]);
      setError(null);
      return;
    }

    let cancelled = false;
    setLoadingMessages(true);
    setError(null);

    void getConversationMessages(conversationId)
      .then((items) => {
        if (cancelled) return;
        setMessages(toChatMessages(items));
      })
      .catch((err) => {
        if (cancelled) return;
        setMessages([]);
        setError(String(err));
      })
      .finally(() => {
        if (!cancelled) setLoadingMessages(false);
      });

    return () => {
      cancelled = true;
    };
  }, [conversationId]);

  async function send(text: string) {
    abortRef.current?.abort();
    const ac = new AbortController();
    abortRef.current = ac;
    setError(null);
    setMessages((prev) => [
      ...prev,
      { role: "user", content: text },
      { role: "assistant", content: "" },
    ]);
    setStreaming(true);

    const projectId = getActiveProjectId();

    try {
      await postChatStream(
        {
          message: text,
          conversation_id: conversationId ?? undefined,
          project_id: projectId,
        },
        (e) => {
          if (e.event === "token") {
            setMessages((prev) => {
              const next = prev.slice();
              const last = next[next.length - 1];
              if (last?.role === "assistant") {
                next[next.length - 1] = {
                  ...last,
                  content: last.content + e.data.text,
                };
              }
              return next;
            });
          } else if (e.event === "done") {
            const nextId = e.data.conversation_id;
            if (nextId !== conversationId) {
              router.replace(`/ai?conversation=${encodeURIComponent(nextId)}`);
            }
            setListRefresh((n) => n + 1);
          } else if (e.event === "error") {
            setError(e.data.message);
          }
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
    <div className="flex h-[calc(100vh-3rem)]" data-testid="ai-chat-view">
      <ConversationList
        activeId={conversationId}
        onSelect={selectConversation}
        refreshKey={listRefresh}
      />
      <section className="flex flex-1 flex-col">
        <header className="border-b border-border px-4 py-3">
          <h1 className="text-sm font-semibold text-ink">AI — modalità avanzata</h1>
          <p className="text-xs text-ink-muted">
            Chat libera con runtime qualificato. Le azioni contestuali vivono nei moduli.
          </p>
        </header>
        <div className="flex-1 space-y-3 overflow-y-auto p-4">
          {loadingMessages && (
            <div className="text-sm text-ink-muted" data-testid="ai-chat-loading">
              Caricamento messaggi…
            </div>
          )}
          {messages.map((m, i) => (
            <MessageBubble key={i} message={m} />
          ))}
          {streaming && (
            <div
              className="flex items-center gap-1 px-2 text-sm text-ink-muted"
              data-testid="ai-chat-streaming"
              aria-live="polite"
              aria-label="Risposta in corso"
            >
              <span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-accent" />
              <span
                className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-accent"
                style={{ animationDelay: "150ms" }}
              />
              <span
                className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-accent"
                style={{ animationDelay: "300ms" }}
              />
            </div>
          )}
          {error && (
            <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </div>
          )}
        </div>
        <InputBox disabled={streaming || loadingMessages} onSend={send} />
      </section>
    </div>
  );
}
