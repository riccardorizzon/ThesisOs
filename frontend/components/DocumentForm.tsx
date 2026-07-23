"use client";

import { useState } from "react";

import type { Document, DocumentUpdateInput } from "@/lib/documentClient";

type Props = {
  document: Document;
  onSubmit: (input: DocumentUpdateInput) => Promise<void>;
  loading?: boolean;
};

// M3 metadata edit only — file content is immutable (re-upload for a new file).
export function DocumentForm({ document, onSubmit, loading }: Props) {
  const [title, setTitle] = useState(document.title ?? "");
  const [author, setAuthor] = useState(document.author ?? "");
  const [language, setLanguage] = useState(document.language ?? "");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    await onSubmit({
      title: title || null,
      author: author || null,
      language: language || null,
      expected_version: document.version,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4" data-testid="document-form">
      <label className="block text-sm">
        <span className="mb-1 block font-medium text-ink">Title</span>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full rounded border border-border-strong px-3 py-2"
        />
      </label>

      <label className="block text-sm">
        <span className="mb-1 block font-medium text-ink">Author</span>
        <input
          value={author}
          onChange={(e) => setAuthor(e.target.value)}
          className="w-full rounded border border-border-strong px-3 py-2"
        />
      </label>

      <label className="block text-sm">
        <span className="mb-1 block font-medium text-ink">Language</span>
        <input
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          placeholder="e.g. it, en"
          className="w-full rounded border border-border-strong px-3 py-2"
        />
      </label>

      <button
        type="submit"
        disabled={loading}
        className="rounded bg-accent px-4 py-2 text-sm font-medium text-ink-inverse hover:bg-accent-muted disabled:opacity-50"
      >
        Save changes
      </button>
    </form>
  );
}
