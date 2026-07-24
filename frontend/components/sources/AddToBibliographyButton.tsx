"use client";

import { useState } from "react";

import { addSourceToBibliography } from "@/lib/sourcesClient";
import type { SourceListItem } from "@/lib/sourcesTypes";

type AddToBibliographyButtonProps = {
  slug: string;
  corpusStatus?: string | null;
  onPromoted?: (source: SourceListItem) => void;
};

export function AddToBibliographyButton({
  slug,
  corpusStatus,
  onPromoted,
}: AddToBibliographyButtonProps) {
  const [promoted, setPromoted] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (corpusStatus !== "candidata" && !promoted) return null;
  if (promoted) {
    return (
      <p className="text-xs font-medium text-success" role="status">
        Aggiunta alla bibliografia
      </p>
    );
  }

  const handlePromote = async () => {
    setBusy(true);
    setError(null);
    try {
      const source = await addSourceToBibliography(slug);
      setPromoted(true);
      onPromoted?.(source);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Impossibile aggiungere la fonte alla bibliografia. Riprova."
      );
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-1">
      <button
        type="button"
        disabled={busy}
        onClick={() => void handlePromote()}
        className="rounded-md bg-accent px-3 py-1.5 text-xs font-medium text-ink-inverse disabled:opacity-50"
      >
        {busy ? "Aggiunta…" : "Aggiungi alla bibliografia"}
      </button>
      {error ? (
        <p className="text-xs text-danger" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}
