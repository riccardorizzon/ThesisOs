"use client";

import { useState } from "react";

import type { Memory, MemoryCreateInput, MemoryKind, MemoryUpdateInput } from "@/lib/memoryClient";
import { MEMORY_KINDS } from "@/lib/memoryStore";

type CreateProps = {
  mode: "create";
  onSubmit: (input: MemoryCreateInput) => Promise<void>;
  loading?: boolean;
};

type EditProps = {
  mode: "edit";
  memory: Memory;
  onSubmit: (input: MemoryUpdateInput) => Promise<void>;
  loading?: boolean;
};

type Props = CreateProps | EditProps;

export function MemoryForm(props: Props) {
  const isCreate = props.mode === "create";
  const memory = !isCreate ? props.memory : null;

  const [kind, setKind] = useState<MemoryKind>(memory?.kind ?? "concept");
  const [title, setTitle] = useState(memory?.title ?? "");
  const [content, setContent] = useState(memory?.content ?? "");
  const [key, setKey] = useState(memory?.key ?? "");
  const [pinned, setPinned] = useState(memory?.pinned ?? false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (isCreate) {
      await props.onSubmit({
        kind,
        title: title || null,
        content,
        key: key || null,
        pinned,
      });
      return;
    }
    await props.onSubmit({
      title: title || null,
      content,
      pinned,
      expected_version: memory!.version,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4" data-testid="memory-form">
      {isCreate && (
        <label className="block text-sm">
          <span className="mb-1 block font-medium text-ink">Kind</span>
          <select
            value={kind}
            onChange={(e) => setKind(e.target.value as MemoryKind)}
            className="w-full rounded border border-border-strong px-3 py-2"
          >
            {MEMORY_KINDS.map((k) => (
              <option key={k} value={k}>
                {k}
              </option>
            ))}
          </select>
        </label>
      )}

      <label className="block text-sm">
        <span className="mb-1 block font-medium text-ink">Title</span>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full rounded border border-border-strong px-3 py-2"
        />
      </label>

      {isCreate && (
        <label className="block text-sm">
          <span className="mb-1 block font-medium text-ink">Key (optional slug)</span>
          <input
            value={key}
            onChange={(e) => setKey(e.target.value)}
            className="w-full rounded border border-border-strong px-3 py-2"
          />
        </label>
      )}

      <label className="block text-sm">
        <span className="mb-1 block font-medium text-ink">Content</span>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required
          rows={8}
          className="w-full rounded border border-border-strong px-3 py-2 font-mono text-sm"
        />
      </label>

      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" checked={pinned} onChange={(e) => setPinned(e.target.checked)} />
        <span>Pinned (included in prompt when operational kind)</span>
      </label>

      <button
        type="submit"
        disabled={props.loading}
        className="rounded bg-accent px-4 py-2 text-sm font-medium text-ink-inverse hover:bg-accent-muted disabled:opacity-50"
      >
        {isCreate ? "Create memory" : "Save changes"}
      </button>
    </form>
  );
}
