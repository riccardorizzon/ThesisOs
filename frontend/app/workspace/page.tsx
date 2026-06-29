"use client";

import { useCallback, useEffect, useState } from "react";

import {
  Chapter,
  ChapterApiError,
  ChapterStatus,
  ChapterVersion,
  chapterClient,
} from "@/lib/chapterClient";

const STATUSES: ChapterStatus[] = ["draft", "review", "approved", "published"];

export default function WorkspacePage() {
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [selected, setSelected] = useState<Chapter | null>(null);
  const [draft, setDraft] = useState("");
  const [versions, setVersions] = useState<ChapterVersion[]>([]);
  const [newTitle, setNewTitle] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const refreshList = useCallback(async () => {
    try {
      setChapters(await chapterClient.list());
    } catch (e) {
      setError(e instanceof Error ? e.message : "failed to load chapters");
    }
  }, []);

  useEffect(() => {
    void refreshList();
  }, [refreshList]);

  async function open(id: string) {
    setError(null);
    try {
      const ch = await chapterClient.get(id);
      setSelected(ch);
      setDraft(ch.content_md ?? "");
      setVersions(await chapterClient.listVersions(id));
    } catch (e) {
      setError(e instanceof Error ? e.message : "failed to open chapter");
    }
  }

  async function create(e: React.FormEvent) {
    e.preventDefault();
    if (!newTitle.trim()) return;
    setError(null);
    try {
      const ch = await chapterClient.create({ title: newTitle.trim() });
      setNewTitle("");
      await refreshList();
      await open(ch.id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "failed to create chapter");
    }
  }

  async function save() {
    if (!selected) return;
    setBusy(true);
    setError(null);
    try {
      const updated = await chapterClient.update(selected.id, {
        content_md: draft,
        expected_version: selected.version,
      });
      setSelected(updated);
      setVersions(await chapterClient.listVersions(updated.id));
      await refreshList();
    } catch (e) {
      if (e instanceof ChapterApiError && e.status === 409) {
        setError("This chapter changed elsewhere — reopen it to get the latest version before saving.");
      } else {
        setError(e instanceof Error ? e.message : "failed to save");
      }
    } finally {
      setBusy(false);
    }
  }

  async function changeStatus(status: ChapterStatus) {
    if (!selected) return;
    setError(null);
    try {
      const updated = await chapterClient.update(selected.id, {
        status,
        expected_version: selected.version,
      });
      setSelected(updated);
      setVersions(await chapterClient.listVersions(updated.id));
      await refreshList();
    } catch (e) {
      setError(e instanceof Error ? e.message : "failed to change status");
    }
  }

  return (
    <section className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Writing Workspace</h1>
        <p className="mt-1 text-sm text-gray-500">
          Draft and revise thesis chapters. Edits are versioned (append-only change stream).
        </p>
      </div>

      {error && (
        <div className="rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 md:grid-cols-[18rem_1fr]">
        <aside className="space-y-3">
          <form className="flex gap-2" onSubmit={create}>
            <input
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="New chapter title"
              className="flex-1 rounded border border-gray-300 px-3 py-2 text-sm"
              data-testid="new-chapter-title"
            />
            <button type="submit" className="rounded bg-gray-900 px-3 py-2 text-sm font-medium text-white hover:bg-gray-800">
              Add
            </button>
          </form>
          <ul className="divide-y divide-gray-100 rounded border border-gray-200">
            {chapters.length === 0 && <li className="px-3 py-2 text-sm text-gray-400">No chapters yet</li>}
            {chapters.map((c) => (
              <li key={c.id}>
                <button
                  type="button"
                  onClick={() => open(c.id)}
                  className={`flex w-full items-center justify-between px-3 py-2 text-left text-sm hover:bg-gray-50 ${
                    selected?.id === c.id ? "bg-gray-100" : ""
                  }`}
                >
                  <span className="truncate">{c.title}</span>
                  <span className="ml-2 shrink-0 text-xs text-gray-400">{c.status}</span>
                </button>
              </li>
            ))}
          </ul>
        </aside>

        <main className="space-y-3">
          {!selected ? (
            <p className="text-sm text-gray-500">Select or create a chapter to start writing.</p>
          ) : (
            <>
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h2 className="text-lg font-medium">{selected.title}</h2>
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <span>v{selected.version}</span>
                  <span>· {selected.word_count} words</span>
                  <select
                    value={selected.status}
                    onChange={(e) => changeStatus(e.target.value as ChapterStatus)}
                    className="rounded border border-gray-300 px-2 py-1 text-xs"
                    aria-label="Chapter status"
                  >
                    {STATUSES.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <textarea
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                className="h-80 w-full rounded border border-gray-300 p-3 font-mono text-sm"
                placeholder="Write in Markdown…"
                data-testid="chapter-editor"
              />
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={save}
                  disabled={busy}
                  className="rounded bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50"
                >
                  {busy ? "Saving…" : "Save"}
                </button>
              </div>

              <details className="rounded border border-gray-200 p-3">
                <summary className="cursor-pointer text-sm font-medium">History ({versions.length})</summary>
                <ul className="mt-2 space-y-1 text-xs text-gray-600">
                  {versions.map((v) => (
                    <li key={v.version} className="flex justify-between">
                      <span>
                        v{v.version} · {v.change_kind}
                      </span>
                      <span className="text-gray-400">{new Date(v.changed_at).toLocaleString()}</span>
                    </li>
                  ))}
                </ul>
              </details>
            </>
          )}
        </main>
      </div>
    </section>
  );
}
