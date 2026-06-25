"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { DocumentErrorBanner } from "@/components/DocumentErrorBanner";
import { useDocumentStore } from "@/lib/documentStore";

const ACCEPT = ".pdf,.epub,.docx";

export default function DocumentUploadPage() {
  const router = useRouter();
  const { upload, loading, error, errorCode, errorStatus, clearError } = useDocumentStore();

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
      router.push(`/documents/${created.id}`);
    } catch {
      // error surfaced via store/banner
    }
  }

  return (
    <section className="mx-auto max-w-xl space-y-6">
      <Link href="/documents" className="text-sm text-gray-500 hover:underline">
        ← Back to list
      </Link>
      <h1 className="text-2xl font-semibold">Upload document</h1>
      <p className="text-sm text-gray-500">PDF, EPUB or DOCX. Parsing runs automatically after upload.</p>

      <DocumentErrorBanner message={error} code={errorCode} status={errorStatus} />
      {error && (
        <button type="button" onClick={clearError} className="text-xs text-gray-500 underline">
          Dismiss
        </button>
      )}

      <form onSubmit={handleSubmit} className="space-y-4" data-testid="document-upload-form">
        <label className="block text-sm">
          <span className="mb-1 block font-medium text-gray-700">File</span>
          <input
            type="file"
            accept={ACCEPT}
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="w-full rounded border border-gray-300 px-3 py-2"
            data-testid="document-file-input"
          />
        </label>

        <label className="block text-sm">
          <span className="mb-1 block font-medium text-gray-700">Title (optional)</span>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full rounded border border-gray-300 px-3 py-2"
          />
        </label>

        <label className="block text-sm">
          <span className="mb-1 block font-medium text-gray-700">Author (optional)</span>
          <input
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
            className="w-full rounded border border-gray-300 px-3 py-2"
          />
        </label>

        <label className="block text-sm">
          <span className="mb-1 block font-medium text-gray-700">Language (optional)</span>
          <input
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            placeholder="e.g. it, en"
            className="w-full rounded border border-gray-300 px-3 py-2"
          />
        </label>

        <button
          type="submit"
          disabled={!file || loading}
          className="rounded bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50"
        >
          {loading ? "Uploading…" : "Upload"}
        </button>
      </form>
    </section>
  );
}
