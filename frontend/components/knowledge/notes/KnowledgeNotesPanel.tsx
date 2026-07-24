"use client";

import { useEffect, useState } from "react";

import {
  memoryClient,
  memoryDisplayTitle,
  type Memory,
  type MemoryVersion,
} from "@/lib/memoryClient";

type EditorState = {
  title: string;
  content: string;
  pinned: boolean;
};

const EMPTY_EDITOR: EditorState = {
  title: "",
  content: "",
  pinned: false,
};

export function KnowledgeNotesPanel() {
  const [notes, setNotes] = useState<Memory[]>([]);
  const [selected, setSelected] = useState<Memory | null>(null);
  const [versions, setVersions] = useState<MemoryVersion[]>([]);
  const [editor, setEditor] = useState<EditorState>(EMPTY_EDITOR);
  const [creating, setCreating] = useState(false);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    void memoryClient
      .list({ kind: "note" })
      .then((items) => {
        if (active) setNotes(items);
      })
      .catch(() => {
        if (active) setError("Impossibile caricare le note. Riprova.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const startCreate = () => {
    setSelected(null);
    setVersions([]);
    setEditor(EMPTY_EDITOR);
    setCreating(true);
    setDeleteConfirm(false);
    setError(null);
  };

  const selectNote = async (note: Memory) => {
    setSelected(note);
    setCreating(false);
    setDeleteConfirm(false);
    setEditor({
      title: note.title ?? "",
      content: note.content,
      pinned: note.pinned,
    });
    setError(null);
    try {
      setVersions(await memoryClient.listVersions(note.id));
    } catch {
      setVersions([]);
      setError("Impossibile caricare la cronologia della nota.");
    }
  };

  const save = async (event: React.FormEvent) => {
    event.preventDefault();
    const title = editor.title.trim();
    const content = editor.content.trim();
    if (!content || busy) return;
    setBusy(true);
    setError(null);
    try {
      if (selected) {
        const updated = await memoryClient.update(selected.id, {
          title: title || null,
          content,
          pinned: editor.pinned,
          expected_version: selected.version,
        });
        setSelected(updated);
        setNotes((current) =>
          current.map((note) => (note.id === updated.id ? updated : note))
        );
        setVersions(await memoryClient.listVersions(updated.id));
      } else {
        const created = await memoryClient.create({
          kind: "note",
          title: title || null,
          content,
          pinned: editor.pinned,
        });
        setNotes((current) => [created, ...current]);
        setSelected(created);
        setCreating(false);
        setVersions([]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Salvataggio non riuscito.");
    } finally {
      setBusy(false);
    }
  };

  const remove = async () => {
    if (!selected || busy) return;
    setBusy(true);
    setError(null);
    try {
      await memoryClient.delete(selected.id);
      setNotes((current) => current.filter((note) => note.id !== selected.id));
      setSelected(null);
      setVersions([]);
      setEditor(EMPTY_EDITOR);
      setDeleteConfirm(false);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Eliminazione della nota non riuscita."
      );
    } finally {
      setBusy(false);
    }
  };

  const showEditor = creating || selected !== null;

  return (
    <section className="mx-auto max-w-content space-y-5" aria-label="Note">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-ink">Note</h1>
          <p className="mt-1 text-sm text-ink-muted">
            Appunti del progetto, separati dai concetti del grafo.
          </p>
        </div>
        <button
          type="button"
          onClick={startCreate}
          className="rounded-md bg-accent px-3 py-2 text-sm font-medium text-ink-inverse"
        >
          Nuova nota
        </button>
      </header>

      {error ? (
        <p className="rounded-md bg-danger/10 px-3 py-2 text-sm text-danger" role="alert">
          {error}
        </p>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-[16rem_minmax(0,1fr)]">
        <div className="rounded-lg border border-border bg-surface p-3">
          {loading ? (
            <p className="text-sm text-ink-muted">Caricamento note…</p>
          ) : notes.length === 0 ? (
            <p className="text-sm text-ink-muted">Nessuna nota ancora</p>
          ) : (
            <ul className="space-y-1">
              {notes.map((note) => (
                <li key={note.id}>
                  <button
                    type="button"
                    onClick={() => void selectNote(note)}
                    className={`w-full rounded-md px-3 py-2 text-left text-sm ${
                      selected?.id === note.id
                        ? "bg-accent-subtle text-accent"
                        : "text-ink hover:bg-surface-muted"
                    }`}
                  >
                    {memoryDisplayTitle(note)}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="rounded-lg border border-border bg-surface p-4">
          {showEditor ? (
            <form className="space-y-4" onSubmit={(event) => void save(event)}>
              <label className="block text-sm font-medium text-ink">
                Titolo nota
                <input
                  value={editor.title}
                  maxLength={200}
                  disabled={busy}
                  onChange={(event) =>
                    setEditor((current) => ({
                      ...current,
                      title: event.target.value,
                    }))
                  }
                  className="mt-1 w-full rounded-md border border-border px-3 py-2 text-sm"
                />
              </label>
              <label className="block text-sm font-medium text-ink">
                Contenuto nota
                <textarea
                  value={editor.content}
                  required
                  rows={10}
                  disabled={busy}
                  onChange={(event) =>
                    setEditor((current) => ({
                      ...current,
                      content: event.target.value,
                    }))
                  }
                  className="mt-1 w-full rounded-md border border-border px-3 py-2 text-sm"
                />
              </label>
              <label className="flex items-center gap-2 text-sm text-ink">
                <input
                  type="checkbox"
                  checked={editor.pinned}
                  disabled={busy}
                  onChange={(event) =>
                    setEditor((current) => ({
                      ...current,
                      pinned: event.target.checked,
                    }))
                  }
                />
                Includi nel contesto AI
              </label>
              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="submit"
                  disabled={busy || !editor.content.trim()}
                  className="rounded-md bg-accent px-3 py-2 text-sm font-medium text-ink-inverse disabled:opacity-50"
                >
                  {selected ? "Salva modifiche" : "Salva nota"}
                </button>
                {selected ? (
                  <button
                    type="button"
                    disabled={busy}
                    onClick={() => setDeleteConfirm(true)}
                    className="rounded-md border border-danger px-3 py-2 text-sm text-danger"
                  >
                    Elimina nota
                  </button>
                ) : null}
              </div>

              {deleteConfirm && selected ? (
                <div className="rounded-md border border-danger/30 bg-danger/5 p-3">
                  <p className="text-sm text-ink">
                    Eliminare definitivamente questa nota?
                  </p>
                  <div className="mt-2 flex gap-2">
                    <button
                      type="button"
                      onClick={() => setDeleteConfirm(false)}
                      className="rounded-md border border-border px-2 py-1 text-xs"
                    >
                      Annulla
                    </button>
                    <button
                      type="button"
                      onClick={() => void remove()}
                      className="rounded-md bg-danger px-2 py-1 text-xs font-medium text-ink-inverse"
                    >
                      Conferma eliminazione nota
                    </button>
                  </div>
                </div>
              ) : null}

              {selected && versions.length > 0 ? (
                <section className="border-t border-border pt-4" aria-label="Cronologia nota">
                  <h2 className="text-sm font-semibold text-ink">Cronologia</h2>
                  <ul className="mt-2 space-y-1 text-xs text-ink-muted">
                    {versions.map((version) => (
                      <li key={version.version}>Versione {version.version}</li>
                    ))}
                  </ul>
                </section>
              ) : null}
            </form>
          ) : (
            <p className="text-sm text-ink-muted">
              Seleziona una nota oppure creane una nuova.
            </p>
          )}
        </div>
      </div>
    </section>
  );
}
