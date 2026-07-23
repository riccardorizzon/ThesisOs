"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { postChatStream, type ChatSource } from "@/lib/api";
import { ConversationList } from "@/components/ConversationList";
import { InputBox } from "@/components/InputBox";
import { MessageBubble } from "@/components/MessageBubble";
import {
  getCompanionResume,
  type CompanionResumePacket,
} from "@/lib/companionClient";
import {
  getConversationMessages,
  type ConversationMessage,
} from "@/lib/conversationClient";
import { getActiveProjectId } from "@/lib/projectPrefs";
import type { ChatMessage } from "@/lib/store";

type ViewMessage = ChatMessage & { sources?: ChatSource[] };

function toChatMessages(items: ConversationMessage[]): ViewMessage[] {
  return items
    .filter((m) => m.role === "user" || m.role === "assistant")
    .map((m) => ({
      role: m.role as "user" | "assistant",
      content: m.content,
    }));
}

/**
 * Thesis Companion chat — companion-first home entry (ADR-0045).
 * The resume packet is the single source of truth for where work resumes.
 * Layer: Business (Product Plane)
 */
export function AiChatView() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const conversationId = searchParams.get("conversation");

  const [messages, setMessages] = useState<ViewMessage[]>([]);
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [resume, setResume] = useState<CompanionResumePacket | null>(null);
  const [loadingResume, setLoadingResume] = useState(false);
  const [resumeError, setResumeError] = useState<string | null>(null);
  const [listRefresh, setListRefresh] = useState(0);
  const abortRef = useRef<AbortController | null>(null);

  const selectConversation = useCallback(
    (id: string) => {
      router.replace(`/?conversation=${encodeURIComponent(id)}`);
    },
    [router]
  );

  useEffect(() => () => abortRef.current?.abort(), []);

  useEffect(() => {
    if (conversationId) {
      setResume(null);
      setResumeError(null);
      setLoadingResume(false);
      return;
    }

    let cancelled = false;
    setLoadingResume(true);
    setResumeError(null);
    void getCompanionResume(getActiveProjectId())
      .then((packet) => {
        if (!cancelled) setResume(packet);
      })
      .catch((err) => {
        if (!cancelled) {
          setResume(null);
          setResumeError(String(err));
        }
      })
      .finally(() => {
        if (!cancelled) setLoadingResume(false);
      });

    return () => {
      cancelled = true;
    };
  }, [conversationId]);

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

  async function send(text: string, visibleText = text) {
    abortRef.current?.abort();
    const ac = new AbortController();
    abortRef.current = ac;
    setError(null);
    setMessages((prev) => [
      ...prev,
      { role: "user", content: visibleText },
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
          } else if (e.event === "replace") {
            setMessages((prev) => {
              const next = prev.slice();
              const last = next[next.length - 1];
              if (last?.role === "assistant") {
                next[next.length - 1] = { ...last, content: e.data.text };
              }
              return next;
            });
          } else if (e.event === "sources") {
            setMessages((prev) => {
              const next = prev.slice();
              const last = next[next.length - 1];
              if (last?.role === "assistant") {
                next[next.length - 1] = { ...last, sources: e.data.sources };
              }
              return next;
            });
          } else if (e.event === "done") {
            const nextId = e.data.conversation_id;
            if (nextId !== conversationId) {
              router.replace(`/?conversation=${encodeURIComponent(nextId)}`);
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
      <section className="flex min-w-0 flex-1 flex-col">
        <header className="border-b border-border px-4 py-3">
          <h1 className="text-sm font-semibold text-ink">Thesis Companion</h1>
          <p className="text-xs text-ink-muted">
            La scrivania per continuare la tesi e lavorare con tutti i moduli.
          </p>
        </header>
        <div className="flex-1 space-y-3 overflow-y-auto p-4">
          {!conversationId && loadingResume && (
            <div
              className="text-sm text-ink-muted"
              data-testid="companion-resume-loading"
              aria-live="polite"
            >
              Caricamento del punto di ripresa…
            </div>
          )}
          {!conversationId && resumeError && (
            <div
              className="rounded-lg border border-border bg-surface-muted px-3 py-2 text-sm text-ink-muted"
              aria-live="polite"
            >
              Il punto di ripresa non è disponibile. Puoi comunque usare la chat.
            </div>
          )}
          {!conversationId && resume && (
            <section
              className="rounded-lg border border-border bg-surface p-4 shadow-sm"
              aria-labelledby="companion-resume-title"
            >
              <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0 space-y-1">
                  <p className="text-xs font-medium uppercase tracking-wide text-ink-muted">
                    Riprendi il lavoro
                  </p>
                  <h2
                    id="companion-resume-title"
                    className="truncate text-base font-semibold text-ink"
                  >
                    {resume.title}
                  </h2>
                  <div className="flex flex-wrap items-center gap-2 text-xs">
                    <span className="font-medium text-accent">
                      {resume.resume.focus_section}
                    </span>
                    <span className="rounded-full bg-surface-muted px-2 py-0.5 text-ink-muted">
                      {resume.resume.focus_status}
                    </span>
                  </div>
                </div>
                <button
                  type="button"
                  className="shrink-0 rounded-md bg-accent px-3 py-2 text-sm font-medium text-ink-inverse hover:opacity-90 disabled:opacity-50"
                  disabled={streaming}
                  onClick={() =>
                    void send(
                      "__companion_open__",
                      resume.continue_prompt || "Continuiamo da ieri",
                    )
                  }
                >
                  Continua da {resume.resume.focus_section}
                </button>
              </div>
              <p className="mt-3 text-sm text-ink-muted">{resume.progress_summary}</p>
              <p className="mt-2 text-sm text-ink">
                <span className="font-medium">Prossima azione:</span>{" "}
                {resume.resume.next_action}
              </p>
              <nav className="mt-3 flex flex-wrap gap-x-4 gap-y-2 border-t border-border pt-3">
                <Link className="text-xs font-medium text-accent hover:underline" href="/writing">
                  <span aria-label="Vai alla scrittura">Scrittura</span>
                </Link>
                <Link className="text-xs font-medium text-accent hover:underline" href="/review">
                  <span aria-label="Vai alla revisione">Revisione</span>
                </Link>
                <Link className="text-xs font-medium text-accent hover:underline" href="/sources">
                  <span aria-label="Vai alle fonti">Fonti</span>
                </Link>
              </nav>
            </section>
          )}
          {loadingMessages && (
            <div className="text-sm text-ink-muted" data-testid="ai-chat-loading">
              Caricamento messaggi…
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i}>
              <MessageBubble message={m} />
              {m.role === "assistant" && m.sources && m.sources.length > 0 && (
                <ul
                  className="ml-2 mt-1 flex flex-wrap gap-2 text-xs text-ink-muted"
                  aria-label="Fonti della risposta"
                >
                  {m.sources.map((source) => (
                    <li
                      key={`${source.document_id}-${source.chunk_id}`}
                      className="rounded-full border border-border bg-surface px-2 py-1"
                    >
                      {source.document_title || "Documento senza titolo"}
                      {source.page_from != null && (
                        <span className="ml-1">p. {source.page_from}</span>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>
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
            <div
              className="rounded-lg bg-danger/10 px-3 py-2 text-sm text-danger"
              aria-live="polite"
            >
              {error}
            </div>
          )}
        </div>
        <InputBox disabled={streaming || loadingMessages} onSend={send} />
      </section>
    </div>
  );
}
