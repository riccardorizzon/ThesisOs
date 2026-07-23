"use client";

import Link from "next/link";

import { MemoryKindBadge } from "@/components/MemoryKindBadge";
import { memoryDisplayTitle, type Memory } from "@/lib/memoryClient";

function formatWhen(iso: string) {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export function MemoryList({ items }: { items: Memory[] }) {
  if (items.length === 0) {
    return <p className="text-sm text-ink-muted">No memories found.</p>;
  }

  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <table className="min-w-full divide-y divide-border text-sm" data-testid="memory-list">
        <thead className="bg-surface-muted text-left text-xs uppercase tracking-wide text-ink-muted">
          <tr>
            <th className="px-4 py-3">Title</th>
            <th className="px-4 py-3">Kind</th>
            <th className="px-4 py-3">Version</th>
            <th className="px-4 py-3">Updated</th>
            <th className="px-4 py-3">Pinned</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border bg-surface">
          {items.map((m) => (
            <tr key={m.id} className="hover:bg-surface-muted">
              <td className="px-4 py-3">
                <Link href={`/memory/${m.id}`} className="font-medium text-ink hover:underline">
                  {memoryDisplayTitle(m)}
                </Link>
              </td>
              <td className="px-4 py-3">
                <MemoryKindBadge kind={m.kind} />
              </td>
              <td className="px-4 py-3 text-ink-muted">v{m.version}</td>
              <td className="px-4 py-3 text-ink-muted">{formatWhen(m.updated_at)}</td>
              <td className="px-4 py-3 text-ink-muted">{m.pinned ? "yes" : "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
