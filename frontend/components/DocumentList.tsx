"use client";

import Link from "next/link";

import { DocumentStatusBadge } from "@/components/DocumentStatusBadge";
import { documentDisplayTitle, type Document } from "@/lib/documentClient";

function formatWhen(iso: string) {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export function DocumentList({ items }: { items: Document[] }) {
  if (items.length === 0) {
    return <p className="text-sm text-ink-muted">No documents found.</p>;
  }

  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <table className="min-w-full divide-y divide-border text-sm" data-testid="document-list">
        <thead className="bg-surface-muted text-left text-xs uppercase tracking-wide text-ink-muted">
          <tr>
            <th className="px-4 py-3">Title</th>
            <th className="px-4 py-3">Type</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Chunks</th>
            <th className="px-4 py-3">Updated</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border bg-surface">
          {items.map((d) => (
            <tr key={d.id} className="hover:bg-surface-muted">
              <td className="px-4 py-3">
                <Link href={`/documents/${d.id}`} className="font-medium text-ink hover:underline">
                  {documentDisplayTitle(d)}
                </Link>
              </td>
              <td className="px-4 py-3 text-ink-muted uppercase">{d.source_type}</td>
              <td className="px-4 py-3">
                <DocumentStatusBadge status={d.status} />
              </td>
              <td className="px-4 py-3 text-ink-muted">{d.chunk_count ?? "—"}</td>
              <td className="px-4 py-3 text-ink-muted">{formatWhen(d.updated_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
