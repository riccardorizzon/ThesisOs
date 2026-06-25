"use client";

import type { DocumentVersion } from "@/lib/documentClient";

function formatWhen(iso: string) {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export function DocumentVersionList({ versions }: { versions: DocumentVersion[] }) {
  if (versions.length === 0) {
    return <p className="text-sm text-gray-500">No version history.</p>;
  }

  return (
    <div className="space-y-3" data-testid="document-version-list">
      {versions.map((v) => (
        <article key={v.version} className="rounded border border-gray-200 p-3">
          <div className="mb-1 flex items-center justify-between text-sm">
            <span className="font-medium">Version {v.version}</span>
            <span className="text-gray-500">{formatWhen(v.changed_at)}</span>
          </div>
          <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-600">
            <span>reason: {v.change_reason}</span>
            {v.parser && <span>parser: {v.parser}</span>}
            {v.chunk_count != null && <span>chunks: {v.chunk_count}</span>}
            {v.page_count != null && <span>pages: {v.page_count}</span>}
          </div>
        </article>
      ))}
      <p className="text-xs text-gray-500">Read-only history. Restore is not available in M3.</p>
    </div>
  );
}
