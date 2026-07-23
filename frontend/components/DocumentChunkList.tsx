"use client";

import type { DocumentChunk } from "@/lib/documentClient";

const PREVIEW_CHARS = 200;

function preview(content: string): string {
  const text = content.trim().replace(/\s+/g, " ");
  return text.length > PREVIEW_CHARS ? `${text.slice(0, PREVIEW_CHARS)}…` : text;
}

// Verification-only chunk preview (M3 spec §11). NOT a corpus search surface.
export function DocumentChunkList({ chunks }: { chunks: DocumentChunk[] }) {
  if (chunks.length === 0) {
    return <p className="text-sm text-ink-muted">No chunks yet (document not parsed).</p>;
  }

  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <table className="min-w-full divide-y divide-border text-sm" data-testid="document-chunk-list">
        <thead className="bg-surface-muted text-left text-xs uppercase tracking-wide text-ink-muted">
          <tr>
            <th className="px-4 py-3">#</th>
            <th className="px-4 py-3">Pages</th>
            <th className="px-4 py-3">Section</th>
            <th className="px-4 py-3">Preview</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border bg-surface">
          {chunks.map((c) => (
            <tr key={c.id} className="align-top hover:bg-surface-muted">
              <td className="px-4 py-3 text-ink-muted">{c.chunk_index}</td>
              <td className="px-4 py-3 text-ink-muted">
                {c.page_from != null ? `${c.page_from}${c.page_to != null ? `–${c.page_to}` : ""}` : "—"}
              </td>
              <td className="px-4 py-3 text-ink-muted">{c.section_path ?? "—"}</td>
              <td className="px-4 py-3 text-ink">{preview(c.content)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
