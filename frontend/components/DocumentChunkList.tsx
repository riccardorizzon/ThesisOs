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
    return <p className="text-sm text-gray-500">No chunks yet (document not parsed).</p>;
  }

  return (
    <div className="overflow-hidden rounded-lg border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200 text-sm" data-testid="document-chunk-list">
        <thead className="bg-gray-50 text-left text-xs uppercase tracking-wide text-gray-500">
          <tr>
            <th className="px-4 py-3">#</th>
            <th className="px-4 py-3">Pages</th>
            <th className="px-4 py-3">Section</th>
            <th className="px-4 py-3">Preview</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100 bg-white">
          {chunks.map((c) => (
            <tr key={c.id} className="align-top hover:bg-gray-50">
              <td className="px-4 py-3 text-gray-600">{c.chunk_index}</td>
              <td className="px-4 py-3 text-gray-600">
                {c.page_from != null ? `${c.page_from}${c.page_to != null ? `–${c.page_to}` : ""}` : "—"}
              </td>
              <td className="px-4 py-3 text-gray-600">{c.section_path ?? "—"}</td>
              <td className="px-4 py-3 text-gray-800">{preview(c.content)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
