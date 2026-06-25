"use client";

import Link from "next/link";
import { useEffect } from "react";

import { DocumentErrorBanner } from "@/components/DocumentErrorBanner";
import { DocumentList } from "@/components/DocumentList";
import type { DocumentSourceType, DocumentStatus } from "@/lib/documentClient";
import {
  DOCUMENT_SOURCE_TYPES,
  DOCUMENT_STATUSES,
  useDocumentStore,
} from "@/lib/documentStore";

export default function DocumentAdminPage() {
  const {
    items,
    loading,
    error,
    errorCode,
    errorStatus,
    listQuery,
    statusFilter,
    sourceTypeFilter,
    fetchList,
    setListQuery,
    setStatusFilter,
    setSourceTypeFilter,
    clearError,
  } = useDocumentStore();

  useEffect(() => {
    void fetchList();
  }, [fetchList]);

  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Document Administration</h1>
          <p className="mt-1 text-sm text-gray-500">
            Import, parse, and inspect source documents (M3 ingestion — not a reader or search workspace).
          </p>
        </div>
        <Link
          href="/documents/upload"
          className="rounded bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800"
        >
          Upload document
        </Link>
      </div>

      <form
        className="flex flex-wrap gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          void fetchList();
        }}
      >
        <input
          value={listQuery}
          onChange={(e) => setListQuery(e.target.value)}
          placeholder="Filter title/filename (not corpus search)"
          className="min-w-[16rem] flex-1 rounded border border-gray-300 px-3 py-2 text-sm"
          data-testid="document-search-input"
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as DocumentStatus | "")}
          className="rounded border border-gray-300 px-3 py-2 text-sm"
          aria-label="Filter by status"
        >
          <option value="">all status</option>
          {DOCUMENT_STATUSES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
        <select
          value={sourceTypeFilter}
          onChange={(e) => setSourceTypeFilter(e.target.value as DocumentSourceType | "")}
          className="rounded border border-gray-300 px-3 py-2 text-sm"
          aria-label="Filter by type"
        >
          <option value="">all types</option>
          {DOCUMENT_SOURCE_TYPES.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
        <button type="submit" className="rounded border border-gray-300 px-3 py-2 text-sm hover:bg-gray-50">
          Apply
        </button>
      </form>

      <DocumentErrorBanner message={error} code={errorCode} status={errorStatus} />
      {error && (
        <button type="button" onClick={clearError} className="text-xs text-gray-500 underline">
          Dismiss
        </button>
      )}

      {loading ? <p className="text-sm text-gray-500">Loading…</p> : <DocumentList items={items} />}
    </section>
  );
}
