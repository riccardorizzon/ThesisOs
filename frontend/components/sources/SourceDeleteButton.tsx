"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { cn } from "@/lib/cn";
import { deleteSource } from "@/lib/sourcesClient";

export type SourceDeleteButtonProps = {
  slug: string;
  title: string;
  /** After delete, navigate here (default: /sources). Pass null to stay on page. */
  redirectTo?: string | null;
  onDeleted?: () => void;
  className?: string;
  variant?: "detail" | "card";
};

export function SourceDeleteButton({
  slug,
  title,
  redirectTo = "/sources",
  onDeleted,
  className,
  variant = "detail",
}: SourceDeleteButtonProps) {
  const router = useRouter();
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleDelete() {
    setBusy(true);
    setError(null);
    try {
      await deleteSource(slug);
      onDeleted?.();
      if (redirectTo) {
        router.push(redirectTo);
        router.refresh();
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Eliminazione fallita");
      setConfirming(false);
    } finally {
      setBusy(false);
    }
  }

  if (confirming) {
    return (
      <div
        className={cn(
          "rounded-lg border border-border bg-surface-muted p-4",
          className
        )}
        data-testid="source-delete-confirm"
      >
        <p className="text-sm text-ink">
          Eliminare <span className="font-medium">{title}</span>? L&apos;azione non
          può essere annullata.
        </p>
        {error && (
          <p className="mt-2 text-sm text-warning" role="alert">
            {error}
          </p>
        )}
        <div className="mt-3 flex flex-wrap gap-2">
          <button
            type="button"
            disabled={busy}
            onClick={() => void handleDelete()}
            className="rounded-md bg-warning px-3 py-1.5 text-sm font-medium text-white hover:bg-warning/90 disabled:opacity-50 cursor-pointer"
            data-testid="source-delete-confirm-yes"
          >
            {busy ? "Eliminazione…" : "Elimina"}
          </button>
          <button
            type="button"
            disabled={busy}
            onClick={() => {
              setConfirming(false);
              setError(null);
            }}
            className="rounded-md border border-border bg-surface px-3 py-1.5 text-sm font-medium text-ink hover:bg-surface-muted cursor-pointer"
            data-testid="source-delete-confirm-no"
          >
            Annulla
          </button>
        </div>
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={() => setConfirming(true)}
      className={cn(
        variant === "detail"
          ? "rounded-md border border-border bg-surface px-4 py-2 text-sm font-medium text-ink-muted hover:border-warning hover:text-warning cursor-pointer"
          : "rounded-md border border-border bg-surface px-2 py-1 text-xs font-medium text-ink-muted hover:border-warning hover:text-warning cursor-pointer",
        className
      )}
      data-testid="source-delete-trigger"
    >
      Elimina fonte
    </button>
  );
}
