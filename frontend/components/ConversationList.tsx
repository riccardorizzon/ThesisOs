"use client";

import { useCallback, useEffect, useState } from "react";

import {
  createConversation,
  listConversations,
  type ConversationSummary,
} from "@/lib/conversationClient";
import { getActiveProjectId } from "@/lib/projectPrefs";

type ConversationListProps = {
  activeId: string | null;
  onSelect: (id: string) => void;
  refreshKey?: number;
};

function formatTitle(conversation: ConversationSummary): string {
  if (conversation.title?.trim()) return conversation.title.trim();
  const date = new Date(conversation.created_at);
  return date.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function ConversationList({
  activeId,
  onSelect,
  refreshKey = 0,
}: ConversationListProps) {
  const [items, setItems] = useState<ConversationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const conversations = await listConversations(getActiveProjectId());
      setItems(conversations);
    } catch (err) {
      setError(String(err));
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load, refreshKey]);

  async function handleNew() {
    setCreating(true);
    setError(null);
    try {
      const created = await createConversation();
      await load();
      onSelect(created.id);
    } catch (err) {
      setError(String(err));
    } finally {
      setCreating(false);
    }
  }

  return (
    <aside
      className="flex w-56 shrink-0 flex-col border-r border-border p-3 text-sm"
      data-testid="conversation-list"
    >
      <div className="mb-2 flex items-center justify-between">
        <div className="font-medium text-ink-muted">Conversazioni</div>
        <button
          type="button"
          className="rounded px-2 py-0.5 text-xs text-accent hover:bg-surface-muted disabled:opacity-50"
          disabled={creating}
          onClick={() => void handleNew()}
        >
          Nuova
        </button>
      </div>
      {loading && (
        <div className="text-xs text-ink-muted" data-testid="conversation-list-loading">
          Caricamento…
        </div>
      )}
      {error && (
        <div className="rounded-lg bg-red-50 px-2 py-1 text-xs text-red-700">{error}</div>
      )}
      {!loading && !error && items.length === 0 && (
        <div className="text-xs text-ink-muted">Nessuna conversazione.</div>
      )}
      <ul className="mt-1 space-y-1 overflow-y-auto">
        {items.map((conversation) => {
          const selected = conversation.id === activeId;
          return (
            <li key={conversation.id}>
              <button
                type="button"
                data-testid={`conversation-item-${conversation.id}`}
                className={`w-full rounded-lg px-3 py-2 text-left transition-colors ${
                  selected
                    ? "bg-surface-muted font-medium text-ink"
                    : "text-ink-muted hover:bg-surface-muted/60"
                }`}
                onClick={() => onSelect(conversation.id)}
              >
                {formatTitle(conversation)}
              </button>
            </li>
          );
        })}
      </ul>
    </aside>
  );
}
