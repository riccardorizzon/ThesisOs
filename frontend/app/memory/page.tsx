"use client";

import Link from "next/link";
import { useEffect } from "react";

import { MemoryErrorBanner } from "@/components/MemoryErrorBanner";
import { MemoryList } from "@/components/MemoryList";
import { useMemoryStore } from "@/lib/memoryStore";

export default function MemoryAdminPage() {
  const { items, loading, error, errorCode, errorStatus, listQuery, fetchList, setListQuery, clearError } =
    useMemoryStore();

  useEffect(() => {
    void fetchList();
  }, [fetchList]);

  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Memory Administration</h1>
          <p className="mt-1 text-sm text-gray-500">
            Inspect and manage thesis memory records (M2 infrastructure — not a knowledge workspace).
          </p>
        </div>
        <Link
          href="/memory/new"
          className="rounded bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800"
        >
          New memory
        </Link>
      </div>

      <form
        className="flex max-w-md gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          void fetchList({ q: listQuery || undefined });
        }}
      >
        <input
          value={listQuery}
          onChange={(e) => setListQuery(e.target.value)}
          placeholder="Filter with q= (substring)"
          className="flex-1 rounded border border-gray-300 px-3 py-2 text-sm"
          data-testid="memory-search-input"
        />
        <button type="submit" className="rounded border border-gray-300 px-3 py-2 text-sm hover:bg-gray-50">
          Search
        </button>
      </form>

      <MemoryErrorBanner message={error} code={errorCode} status={errorStatus} />
      {error && (
        <button type="button" onClick={clearError} className="text-xs text-gray-500 underline">
          Dismiss
        </button>
      )}

      {loading ? <p className="text-sm text-gray-500">Loading…</p> : <MemoryList items={items} />}
    </section>
  );
}
