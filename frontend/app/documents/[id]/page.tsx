"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { DocumentErrorBanner } from "@/components/DocumentErrorBanner";
import { DocumentForm } from "@/components/DocumentForm";
import { DocumentStatusBadge } from "@/components/DocumentStatusBadge";
import { DocumentVersionList } from "@/components/DocumentVersionList";
import { DocumentApiError, documentDisplayTitle } from "@/lib/documentClient";
import { useDocumentStore } from "@/lib/documentStore";

export default function DocumentDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const router = useRouter();
  const [editing, setEditing] = useState(false);

  const {
    selected,
    versions,
    loading,
    error,
    errorCode,
    errorStatus,
    fetchOne,
    fetchVersions,
    update,
    remove,
    reparse,
    clearError,
    clearSelected,
  } = useDocumentStore();

  useEffect(() => {
    if (!id) return;
    void fetchOne(id);
    void fetchVersions(id);
    return () => clearSelected();
  }, [id, fetchOne, fetchVersions, clearSelected]);

  async function handleUpdate(input: Parameters<typeof update>[1]) {
    if (!selected) return;
    try {
      await update(selected.id, input);
      setEditing(false);
      await fetchVersions(selected.id);
    } catch (err) {
      if (err instanceof DocumentApiError && err.status === 409) return;
    }
  }

  async function handleReparse() {
    if (!selected) return;
    try {
      await reparse(selected.id);
      await fetchVersions(selected.id);
    } catch {
      // surfaced via banner
    }
  }

  async function handleDelete() {
    if (!selected) return;
    if (!window.confirm(`Delete "${documentDisplayTitle(selected)}"? This cannot be undone.`)) return;
    try {
      await remove(selected.id);
      router.push("/documents");
    } catch (err) {
      if (err instanceof DocumentApiError && (err.status === 400 || err.status === 404)) return;
    }
  }

  if (loading && !selected) {
    return <p className="text-sm text-gray-500">Loading…</p>;
  }

  if (!selected) {
    return (
      <section className="space-y-4">
        <Link href="/documents" className="text-sm text-gray-500 hover:underline">
          ← Back to list
        </Link>
        <DocumentErrorBanner message={error} code={errorCode} status={errorStatus} />
      </section>
    );
  }

  return (
    <section className="mx-auto max-w-3xl space-y-8">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <Link href="/documents" className="text-sm text-gray-500 hover:underline">
            ← Back to list
          </Link>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <h1 className="text-2xl font-semibold">{documentDisplayTitle(selected)}</h1>
            <span className="text-xs text-gray-500 uppercase">{selected.source_type}</span>
            <DocumentStatusBadge status={selected.status} />
            <span className="text-sm text-gray-500">v{selected.version}</span>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setEditing((v) => !v)}
            className="rounded border border-gray-300 px-3 py-1.5 text-sm hover:bg-gray-50"
          >
            {editing ? "Cancel edit" : "Edit"}
          </button>
          <button
            type="button"
            onClick={() => void handleReparse()}
            className="rounded border border-gray-300 px-3 py-1.5 text-sm hover:bg-gray-50"
            data-testid="document-reparse-button"
          >
            Re-parse
          </button>
          <button
            type="button"
            onClick={() => void handleDelete()}
            className="rounded border border-red-300 px-3 py-1.5 text-sm text-red-700 hover:bg-red-50"
            data-testid="document-delete-button"
          >
            Delete
          </button>
        </div>
      </div>

      <DocumentErrorBanner message={error} code={errorCode} status={errorStatus} />
      {error && (
        <button type="button" onClick={clearError} className="text-xs text-gray-500 underline">
          Dismiss
        </button>
      )}

      {selected.status === "failed" && selected.error_message && (
        <div className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-800">
          Parse failed: {selected.error_message}
        </div>
      )}

      {editing ? (
        <DocumentForm document={selected} onSubmit={handleUpdate} loading={loading} />
      ) : (
        <div className="grid grid-cols-2 gap-4 text-sm">
          <Meta label="Author" value={selected.author ?? "—"} />
          <Meta label="Language" value={selected.language ?? "—"} />
          <Meta label="Pages" value={selected.page_count != null ? String(selected.page_count) : "—"} />
          <Meta label="Chunks" value={selected.chunk_count != null ? String(selected.chunk_count) : "—"} />
          <Meta label="Parser" value={selected.parser ?? "—"} />
          <Meta label="Filename" value={selected.original_filename ?? "—"} />
        </div>
      )}

      <div>
        <Link
          href={`/documents/${selected.id}/chunks`}
          className="text-sm font-medium text-gray-900 hover:underline"
        >
          View chunks ({selected.chunk_count ?? 0}) →
        </Link>
      </div>

      <div>
        <h2 className="mb-3 text-lg font-medium">Version history</h2>
        <DocumentVersionList versions={versions} />
      </div>
    </section>
  );
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded border border-gray-200 px-3 py-2">
      <div className="text-xs uppercase tracking-wide text-gray-500">{label}</div>
      <div className="text-gray-800">{value}</div>
    </div>
  );
}
