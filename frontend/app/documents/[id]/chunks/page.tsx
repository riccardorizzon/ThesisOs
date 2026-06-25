"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect } from "react";

import { DocumentChunkList } from "@/components/DocumentChunkList";
import { DocumentErrorBanner } from "@/components/DocumentErrorBanner";
import { useDocumentStore } from "@/lib/documentStore";

export default function DocumentChunksPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;

  const { chunks, error, errorCode, errorStatus, fetchChunks, clearSelected } = useDocumentStore();

  useEffect(() => {
    if (!id) return;
    void fetchChunks(id);
    return () => clearSelected();
  }, [id, fetchChunks, clearSelected]);

  return (
    <section className="space-y-6">
      <Link href={`/documents/${id}`} className="text-sm text-gray-500 hover:underline">
        ← Back to document
      </Link>
      <div>
        <h1 className="text-2xl font-semibold">Chunks</h1>
        <p className="mt-1 text-sm text-gray-500">
          Parse output for verification only — ordered by index, no relevance ranking, no search.
        </p>
      </div>

      <DocumentErrorBanner message={error} code={errorCode} status={errorStatus} />
      <DocumentChunkList chunks={chunks} />
    </section>
  );
}
