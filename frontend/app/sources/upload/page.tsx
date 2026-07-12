"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { DocumentErrorBanner } from "@/components/DocumentErrorBanner";
import { cn } from "@/lib/cn";
import { useDocumentStore } from "@/lib/documentStore";

const ACCEPT = ".pdf,.epub,.docx";

const inputClassName = cn(
  "w-full rounded-md border border-border bg-surface px-3 py-2 text-sm text-ink",
  "placeholder:text-ink-subtle",
  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
);

export default function SourceUploadPage() {
  const router = useRouter();
  const { upload, loading, error, errorCode, errorStatus, clearError } =
    useDocumentStore();

  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [language, setLanguage] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;
    try {
      const created = await upload({
        file,
        title: title || null,
        author: author || null,
        language: language || null,
      });
      router.push("/sources");
    } catch {
      // error surfaced via store/banner
    }
  }

  return (
    <div className="mx-auto max-w-content">
      <Link
        href="/sources"
        className="inline-block text-sm font-medium text-accent underline-offset-2 hover:underline cursor-pointer"
      >
        ← Torna a Sources
      </Link>

      <header className="mt-4 mb-8">
        <h1 className="text-2xl font-semibold tracking-tight text-ink">
          Aggiungi fonte
        </h1>
        <p className="mt-1 max-w-prose text-sm text-ink-muted">
          Carica un PDF, EPUB o DOCX. Dopo il caricamento la fonte viene analizzata
          automaticamente e aggiunta al corpus.
        </p>
      </header>

      <section className="mx-auto max-w-xl space-y-6">
        <DocumentErrorBanner
          message={error}
          code={errorCode}
          status={errorStatus}
        />
        {error && (
          <button
            type="button"
            onClick={clearError}
            className="text-xs text-ink-subtle underline cursor-pointer"
          >
            Chiudi
          </button>
        )}

        <form
          onSubmit={handleSubmit}
          className="space-y-4 rounded-lg border border-border bg-surface p-6 shadow-sm"
          data-testid="source-upload-form"
        >
          <label className="block text-sm">
            <span className="mb-1 block font-medium text-ink">File</span>
            <input
              type="file"
              accept={ACCEPT}
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className={inputClassName}
              data-testid="source-file-input"
            />
          </label>

          <label className="block text-sm">
            <span className="mb-1 block font-medium text-ink">
              Titolo (opzionale)
            </span>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className={inputClassName}
            />
          </label>

          <label className="block text-sm">
            <span className="mb-1 block font-medium text-ink">
              Autore (opzionale)
            </span>
            <input
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
              className={inputClassName}
            />
          </label>

          <label className="block text-sm">
            <span className="mb-1 block font-medium text-ink">
              Lingua (opzionale)
            </span>
            <input
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              placeholder="es. it, en"
              className={inputClassName}
            />
          </label>

          <button
            type="submit"
            disabled={!file || loading}
            className={cn(
              "rounded-md bg-accent px-4 py-2 text-sm font-medium text-white",
              "transition-colors duration-200 hover:bg-accent-muted",
              "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent",
              "disabled:cursor-not-allowed disabled:opacity-50 cursor-pointer"
            )}
          >
            {loading ? "Caricamento…" : "Aggiungi fonte"}
          </button>
        </form>
      </section>
    </div>
  );
}
