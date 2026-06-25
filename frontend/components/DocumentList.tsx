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
    return <p className="text-sm text-gray-500">No documents found.</p>;
  }

  return (
    <div className="overflow-hidden rounded-lg border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200 text-sm" data-testid="document-list">
        <thead className="bg-gray-50 text-left text-xs uppercase tracking-wide text-gray-500">
          <tr>
            <th className="px-4 py-3">Title</th>
            <th className="px-4 py-3">Type</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Chunks</th>
            <th className="px-4 py-3">Updated</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100 bg-white">
          {items.map((d) => (
            <tr key={d.id} className="hover:bg-gray-50">
              <td className="px-4 py-3">
                <Link href={`/documents/${d.id}`} className="font-medium text-gray-900 hover:underline">
                  {documentDisplayTitle(d)}
                </Link>
              </td>
              <td className="px-4 py-3 text-gray-600 uppercase">{d.source_type}</td>
              <td className="px-4 py-3">
                <DocumentStatusBadge status={d.status} />
              </td>
              <td className="px-4 py-3 text-gray-600">{d.chunk_count ?? "—"}</td>
              <td className="px-4 py-3 text-gray-600">{formatWhen(d.updated_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
