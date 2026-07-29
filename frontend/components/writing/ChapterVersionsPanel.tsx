"use client";

import { useCallback, useEffect, useState } from "react";

import { cn } from "@/lib/cn";
import {
  ChapterApiError,
  chapterClient,
  type Chapter,
  type ChapterVersion,
} from "@/lib/chapterClient";

export type ChapterVersionsPanelProps = {
  open: boolean;
  chapterId: string;
  expectedVersion: number;
  onClose: () => void;
  onRestored: (chapter: Chapter) => void;
  onConflict?: () => void;
  className?: string;
};

export function ChapterVersionsPanel({
  open,
  chapterId,
  expectedVersion,
  onClose,
  onRestored,
  onConflict,
  className,
}: ChapterVersionsPanelProps) {
  const [versions, setVersions] = useState<ChapterVersion[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirmVersion, setConfirmVersion] = useState<ChapterVersion | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!open) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    setConfirmVersion(null);
    void chapterClient
      .listVersions(chapterId)
      .then((rows) => {
        if (!cancelled) {
          setVersions([...rows].sort((a, b) => b.version - a.version));
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Cronologia non disponibile.");
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [chapterId, open]);

  const handleRestore = useCallback(async () => {
    if (!confirmVersion || busy) return;
    setBusy(true);
    setError(null);
    try {
      const updated = await chapterClient.update(chapterId, {
        content_md: confirmVersion.content_md ?? "",
        expected_version: expectedVersion,
      });
      onRestored(updated);
      setConfirmVersion(null);
      onClose();
    } catch (err) {
      if (err instanceof ChapterApiError && err.status === 409) {
        setConfirmVersion(null);
        onConflict?.();
      } else {
        setError(err instanceof Error ? err.message : "Ripristino non riuscito.");
      }
    } finally {
      setBusy(false);
    }
  }, [busy, chapterId, confirmVersion, expectedVersion, onClose, onConflict, onRestored]);

  if (!open) return null;

  return (
    <div
      className={cn(
        "border-t border-border bg-surface-muted px-4 py-3",
        className
      )}
      data-testid="chapter-versions-panel"
    >
      <div className="mb-2 flex items-center justify-between gap-2">
        <h3 className="text-sm font-semibold text-ink">Cronologia versioni</h3>
        <button
          type="button"
          onClick={onClose}
          className="rounded px-2 py-1 text-xs text-ink-muted hover:text-ink"
          data-testid="chapter-versions-close"
        >
          Chiudi
        </button>
      </div>

      {loading ? (
        <p className="text-xs text-ink-muted">Caricamento…</p>
      ) : error ? (
        <p className="text-xs text-danger" role="alert">
          {error}
        </p>
      ) : versions.length === 0 ? (
        <p className="text-xs text-ink-muted">Nessuna versione precedente.</p>
      ) : (
        <ul className="max-h-40 space-y-1 overflow-y-auto">
          {versions.map((version) => (
            <li
              key={version.version}
              className="flex items-center justify-between gap-2 rounded-md border border-border bg-surface px-2 py-1.5"
            >
              <div className="min-w-0">
                <p className="truncate text-xs font-medium text-ink">
                  Versione {version.version} · {version.change_kind}
                </p>
                <p className="truncate text-[11px] text-ink-subtle">
                  {new Date(version.changed_at).toLocaleString()} · {version.title}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setConfirmVersion(version)}
                className="shrink-0 rounded border border-border px-2 py-1 text-[11px] text-ink hover:bg-surface-muted"
                data-testid={`chapter-version-restore-${version.version}`}
              >
                Ripristina
              </button>
            </li>
          ))}
        </ul>
      )}

      {confirmVersion ? (
        <div
          className="mt-3 rounded-md border border-border bg-surface p-3"
          data-testid="chapter-version-restore-dialog"
        >
          <p className="text-xs text-ink">
            Ripristinare il contenuto della versione {confirmVersion.version}? Le
            modifiche non salvate nell&apos;editor verranno sostituite.
          </p>
          <div className="mt-2 flex justify-end gap-2">
            <button
              type="button"
              disabled={busy}
              onClick={() => setConfirmVersion(null)}
              className="rounded px-2 py-1 text-xs text-ink-muted"
            >
              Annulla
            </button>
            <button
              type="button"
              disabled={busy}
              onClick={() => void handleRestore()}
              className="rounded bg-accent px-2 py-1 text-xs font-medium text-ink-inverse disabled:opacity-50"
              data-testid="chapter-version-restore-confirm"
            >
              {busy ? "Ripristino…" : "Conferma"}
            </button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
