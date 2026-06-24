"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { MemoryErrorBanner } from "@/components/MemoryErrorBanner";
import { MemoryForm } from "@/components/MemoryForm";
import { MemoryKindBadge } from "@/components/MemoryKindBadge";
import { MemoryVersionList } from "@/components/MemoryVersionList";
import { MemoryApiError, memoryDisplayTitle } from "@/lib/memoryClient";
import { useMemoryStore } from "@/lib/memoryStore";

export default function MemoryDetailPage() {
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
    clearError,
    clearSelected,
  } = useMemoryStore();

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
      if (err instanceof MemoryApiError && err.status === 409) return;
    }
  }

  async function handleDelete() {
    if (!selected) return;
    if (!window.confirm(`Delete memory "${memoryDisplayTitle(selected)}"? This cannot be undone.`)) return;
    try {
      await remove(selected.id);
      router.push("/memory");
    } catch (err) {
      if (err instanceof MemoryApiError && (err.status === 400 || err.status === 404)) return;
    }
  }

  if (loading && !selected) {
    return <p className="text-sm text-gray-500">Loading…</p>;
  }

  if (!selected && errorStatus === 404) {
    return (
      <section className="space-y-4">
        <Link href="/memory" className="text-sm text-gray-500 hover:underline">
          ← Back to list
        </Link>
        <MemoryErrorBanner message={error} code={errorCode} status={errorStatus} />
      </section>
    );
  }

  if (!selected) {
    return (
      <section className="space-y-4">
        <MemoryErrorBanner message={error} code={errorCode} status={errorStatus} />
      </section>
    );
  }

  return (
    <section className="mx-auto max-w-3xl space-y-8">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <Link href="/memory" className="text-sm text-gray-500 hover:underline">
            ← Back to list
          </Link>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <h1 className="text-2xl font-semibold">{memoryDisplayTitle(selected)}</h1>
            <MemoryKindBadge kind={selected.kind} />
            <span className="text-sm text-gray-500">v{selected.version}</span>
            {selected.pinned && <span className="text-xs text-amber-700">pinned</span>}
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
            onClick={() => void handleDelete()}
            className="rounded border border-red-300 px-3 py-1.5 text-sm text-red-700 hover:bg-red-50"
            data-testid="memory-delete-button"
          >
            Delete
          </button>
        </div>
      </div>

      <MemoryErrorBanner message={error} code={errorCode} status={errorStatus} />
      {error && (
        <button type="button" onClick={clearError} className="text-xs text-gray-500 underline">
          Dismiss
        </button>
      )}

      {editing ? (
        <MemoryForm mode="edit" memory={selected} onSubmit={handleUpdate} loading={loading} />
      ) : (
        <div className="space-y-6">
          <div>
            <h2 className="mb-2 text-sm font-medium text-gray-700">Content</h2>
            <pre className="whitespace-pre-wrap rounded-lg border border-gray-200 bg-gray-50 p-4 text-sm">
              {selected.content}
            </pre>
          </div>
          <div>
            <h2 className="mb-2 text-sm font-medium text-gray-700">Metadata</h2>
            <pre className="overflow-x-auto rounded-lg border border-gray-200 bg-gray-50 p-4 text-xs">
              {JSON.stringify(selected.metadata ?? {}, null, 2)}
            </pre>
          </div>
        </div>
      )}

      <div>
        <h2 className="mb-3 text-lg font-medium">Version history</h2>
        <MemoryVersionList versions={versions} />
      </div>
    </section>
  );
}
