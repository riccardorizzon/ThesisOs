"use client";

import { useCallback, useEffect, useState } from "react";

import {
  createConversation,
  deleteConversation,
  listConversations,
  renameConversation,
  type ConversationSummary,
} from "@/lib/conversationClient";
import { getActiveProjectId } from "@/lib/projectPrefs";

type ConversationListProps = {
  activeId: string | null;
  onSelect: (id: string) => void;
  onDeleted?: (id: string) => void;
  refreshKey?: number;
};

const PLACEHOLDER_TITLES = new Set(["New Conversation", "Nuova conversazione"]);

function formatTitle(conversation: ConversationSummary): string {
  const title = conversation.title?.trim();
  if (title && !PLACEHOLDER_TITLES.has(title)) return title;
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
  onDeleted,
  refreshKey = 0,
}: ConversationListProps) {
  const [items, setItems] = useState<ConversationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [actionId, setActionId] = useState<string | null>(null);
  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [renameTitle, setRenameTitle] = useState("");
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);

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

  async function handleRename(conversationId: string) {
    const title = renameTitle.trim();
    if (!title) return;
    setBusyId(conversationId);
    setError(null);
    try {
      const updated = await renameConversation(
        conversationId,
        title,
        getActiveProjectId()
      );
      setItems((current) =>
        current.map((item) => (item.id === conversationId ? updated : item))
      );
      setRenamingId(null);
      setRenameTitle("");
      setActionId(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Rinomina non riuscita.");
    } finally {
      setBusyId(null);
    }
  }

  async function handleDelete(conversationId: string) {
    setBusyId(conversationId);
    setError(null);
    try {
      await deleteConversation(conversationId, getActiveProjectId());
      setItems((current) => current.filter((item) => item.id !== conversationId));
      setDeleteId(null);
      setActionId(null);
      onDeleted?.(conversationId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Eliminazione non riuscita.");
    } finally {
      setBusyId(null);
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
        <div className="rounded-lg bg-danger/10 px-2 py-1 text-xs text-danger">{error}</div>
      )}
      {!loading && !error && items.length === 0 && (
        <div className="text-xs text-ink-muted">Nessuna conversazione.</div>
      )}
      <ul className="mt-1 space-y-1 overflow-y-auto">
        {items.map((conversation) => {
          const selected = conversation.id === activeId;
          const title = formatTitle(conversation);
          return (
            <li key={conversation.id} className="relative">
              <div
                className={`flex items-center rounded-lg transition-colors ${
                  selected
                    ? "bg-surface-muted font-medium text-ink"
                    : "text-ink-muted hover:bg-surface-muted/60"
                }`}
              >
                <button
                  type="button"
                  data-testid={`conversation-item-${conversation.id}`}
                  className={`min-w-0 flex-1 truncate px-3 py-2 text-left ${
                    selected ? "font-medium" : ""
                  }`}
                  onClick={() => {
                    setActionId(null);
                    onSelect(conversation.id);
                  }}
                >
                  {title}
                </button>
                <button
                  type="button"
                  aria-label={`Azioni per la conversazione ${title}`}
                  aria-expanded={actionId === conversation.id}
                  onClick={() =>
                    setActionId((current) =>
                      current === conversation.id ? null : conversation.id
                    )
                  }
                  className="mr-1 rounded px-2 py-1 text-ink-subtle hover:bg-surface"
                >
                  <span aria-hidden="true">•••</span>
                </button>
              </div>

              {actionId === conversation.id ? (
                <div className="absolute right-1 z-20 mt-1 w-28 rounded-md border border-border bg-surface p-1 shadow-md">
                  <button
                    type="button"
                    className="w-full rounded px-2 py-1 text-left text-xs hover:bg-surface-muted"
                    onClick={() => {
                      setRenamingId(conversation.id);
                      setRenameTitle(
                        PLACEHOLDER_TITLES.has(conversation.title?.trim() ?? "")
                          ? ""
                          : conversation.title?.trim() ?? ""
                      );
                    }}
                  >
                    Rinomina
                  </button>
                  <button
                    type="button"
                    className="w-full rounded px-2 py-1 text-left text-xs text-danger hover:bg-danger/10"
                    onClick={() => {
                      setDeleteId(conversation.id);
                      setActionId(null);
                    }}
                  >
                    Elimina
                  </button>
                </div>
              ) : null}

              {renamingId === conversation.id ? (
                <form
                  className="mt-1 space-y-1 rounded-md border border-border bg-surface p-2"
                  onSubmit={(event) => {
                    event.preventDefault();
                    void handleRename(conversation.id);
                  }}
                >
                  <label className="block text-xs text-ink-muted">
                    Nuovo titolo conversazione
                    <input
                      value={renameTitle}
                      maxLength={120}
                      disabled={busyId === conversation.id}
                      onChange={(event) => setRenameTitle(event.target.value)}
                      className="mt-1 w-full rounded border border-border px-2 py-1 text-xs text-ink"
                      autoFocus
                    />
                  </label>
                  <div className="flex justify-end gap-1">
                    <button
                      type="button"
                      className="rounded px-2 py-1 text-xs text-ink-muted"
                      onClick={() => setRenamingId(null)}
                    >
                      Annulla
                    </button>
                    <button
                      type="submit"
                      disabled={!renameTitle.trim() || busyId === conversation.id}
                      className="rounded bg-accent px-2 py-1 text-xs text-ink-inverse disabled:opacity-50"
                    >
                      Salva titolo
                    </button>
                  </div>
                </form>
              ) : null}
            </li>
          );
        })}
      </ul>

      {deleteId ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-ink/50 p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="delete-conversation-title"
        >
          <div className="w-full max-w-sm rounded-lg border border-border bg-surface p-5 shadow-lg">
            <h2 id="delete-conversation-title" className="font-semibold text-ink">
              Eliminare questa conversazione?
            </h2>
            <p className="mt-2 text-sm text-ink-muted">
              I messaggi della conversazione verranno rimossi definitivamente.
            </p>
            <div className="mt-5 flex justify-end gap-2">
              <button
                type="button"
                disabled={busyId === deleteId}
                onClick={() => setDeleteId(null)}
                className="rounded-md border border-border px-3 py-2 text-sm text-ink-muted"
              >
                Annulla
              </button>
              <button
                type="button"
                disabled={busyId === deleteId}
                onClick={() => void handleDelete(deleteId)}
                className="rounded-md bg-danger px-3 py-2 text-sm font-medium text-ink-inverse disabled:opacity-50"
              >
                Conferma eliminazione conversazione
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </aside>
  );
}
