"use client";

import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { cn } from "@/lib/cn";
import {
  documentClient,
  documentDisplayTitle,
  type Document,
  type DocumentStatus,
} from "@/lib/documentClient";

const PENDING_STATUSES = new Set<DocumentStatus>(["uploaded", "processing"]);
const POLL_MS = 3_000;

const STATUS_LABELS: Record<DocumentStatus, string> = {
  uploaded: "Caricato",
  processing: "Indicizzazione in corso",
  parsed: "Indicizzato",
  failed: "Indicizzazione fallita",
};

export type DocumentIndexStatusBannerProps = {
  className?: string;
};

function isPending(status: DocumentStatus): boolean {
  return PENDING_STATUSES.has(status);
}

/**
 * Shows document indexing progress after upload — polls until parsed or failed.
 * Reads optional `document` query param or any in-flight documents in the corpus.
 * Layer: Business (Product Plane)
 */
export function DocumentIndexStatusBanner({ className }: DocumentIndexStatusBannerProps) {
  const searchParams = useSearchParams();
  const trackedId = searchParams.get("document");

  const [documents, setDocuments] = useState<Document[]>([]);
  const [dismissed, setDismissed] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      if (trackedId) {
        const doc = await documentClient.get(trackedId);
        setDocuments([doc]);
        setLoadError(null);
        return;
      }

      const all = await documentClient.list();
      const pending = all.filter((doc) => isPending(doc.status));
      setDocuments(pending);
      setLoadError(null);
    } catch (err) {
      setLoadError(
        err instanceof Error ? err.message : "Impossibile verificare lo stato indicizzazione"
      );
    }
  }, [trackedId]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  useEffect(() => {
    const hasPending = documents.some((doc) => isPending(doc.status));
    if (!hasPending) return;

    const timer = window.setInterval(() => {
      void refresh();
    }, POLL_MS);
    return () => window.clearInterval(timer);
  }, [documents, refresh]);

  if (dismissed) return null;

  if (loadError) {
    return (
      <div
        role="status"
        className={cn(
          "rounded-md border border-warning/30 bg-warning/10 px-4 py-2 text-sm text-warning",
          className
        )}
        data-testid="writing-index-status-error"
      >
        {loadError}
      </div>
    );
  }

  if (documents.length === 0) return null;

  const pending = documents.filter((doc) => isPending(doc.status));
  const failed = documents.filter((doc) => doc.status === "failed");
  const parsed = documents.filter((doc) => doc.status === "parsed");

  if (pending.length === 0 && failed.length === 0 && parsed.length === 0) {
    return null;
  }

  const showDismiss = pending.length === 0;

  return (
    <div
      role="status"
      aria-live="polite"
      className={cn(
        "rounded-md border px-4 py-3 text-sm",
        pending.length > 0
          ? "border-accent/30 bg-accent-subtle/40 text-ink"
          : failed.length > 0
            ? "border-warning/30 bg-warning/10 text-warning"
            : "border-success/30 bg-success/10 text-success",
        className
      )}
      data-testid="writing-index-status-banner"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 space-y-1">
          {pending.map((doc) => (
            <p key={doc.id} data-testid={`writing-index-pending-${doc.id}`}>
              <span className="font-medium">{documentDisplayTitle(doc)}</span>
              {" — "}
              {STATUS_LABELS[doc.status]}
              {doc.chunk_count != null && doc.status === "processing"
                ? ` (${doc.chunk_count} chunk)`
                : ""}
            </p>
          ))}
          {failed.map((doc) => (
            <p key={doc.id} data-testid={`writing-index-failed-${doc.id}`}>
              <span className="font-medium">{documentDisplayTitle(doc)}</span>
              {" — "}
              {STATUS_LABELS.failed}
              {doc.error_message ? `: ${doc.error_message}` : ""}
            </p>
          ))}
          {pending.length === 0 &&
            failed.length === 0 &&
            parsed.map((doc) => (
              <p key={doc.id} data-testid={`writing-index-parsed-${doc.id}`}>
                <span className="font-medium">{documentDisplayTitle(doc)}</span>
                {" — "}
                {STATUS_LABELS.parsed}
                {doc.chunk_count != null ? ` (${doc.chunk_count} chunk)` : ""}
              </p>
            ))}
        </div>
        {showDismiss && (
          <button
            type="button"
            onClick={() => setDismissed(true)}
            className="shrink-0 text-xs text-ink-muted underline cursor-pointer"
            data-testid="writing-index-status-dismiss"
          >
            Chiudi
          </button>
        )}
      </div>
    </div>
  );
}
