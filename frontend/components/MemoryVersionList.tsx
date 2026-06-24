"use client";

import type { MemoryVersion } from "@/lib/memoryClient";

function formatWhen(iso: string) {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export function MemoryVersionList({ versions }: { versions: MemoryVersion[] }) {
  if (versions.length === 0) {
    return <p className="text-sm text-gray-500">No version history.</p>;
  }

  return (
    <div className="space-y-3" data-testid="memory-version-list">
      {versions.map((v) => (
        <article key={v.version} className="rounded border border-gray-200 p-3">
          <div className="mb-2 flex items-center justify-between text-sm">
            <span className="font-medium">Version {v.version}</span>
            <span className="text-gray-500">{formatWhen(v.changed_at)}</span>
          </div>
          {v.title && <p className="mb-1 text-sm font-medium text-gray-700">{v.title}</p>}
          <pre className="whitespace-pre-wrap rounded bg-gray-50 p-2 text-xs text-gray-800">{v.content}</pre>
        </article>
      ))}
      <p className="text-xs text-gray-500">Read-only history. Restore is not available in M2.</p>
    </div>
  );
}
