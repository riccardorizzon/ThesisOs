"use client";

import { useCallback, useState } from "react";

import { cn } from "@/lib/cn";
import { chapterClient } from "@/lib/chapterClient";

export type ExportMenuProps = {
  chapterId: string | null | undefined;
  /** Disables per-chapter export only; manuscript export stays available. */
  chapterExportDisabled?: boolean;
  disabled?: boolean;
  onError?: () => void;
  className?: string;
};

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

/** Chapter + manuscript export actions. */
export function ExportMenu({
  chapterId,
  chapterExportDisabled = false,
  disabled = false,
  onError,
  className,
}: ExportMenuProps) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);

  const handleExportMarkdown = useCallback(async () => {
    if (!chapterId || chapterExportDisabled) return;
    setBusy(true);
    setOpen(false);
    try {
      const blob = await chapterClient.exportMarkdown(chapterId);
      downloadBlob(blob, `${chapterId}.md`);
    } catch {
      onError?.();
    } finally {
      setBusy(false);
    }
  }, [chapterExportDisabled, chapterId, onError]);

  const handleExportManuscript = useCallback(async () => {
    setBusy(true);
    setOpen(false);
    try {
      const blob = await chapterClient.exportManuscriptMarkdown();
      downloadBlob(blob, "manuscript.md");
    } catch {
      onError?.();
    } finally {
      setBusy(false);
    }
  }, [onError]);

  const triggerDisabled = disabled || busy;
  const chapterItemDisabled = busy || !chapterId || chapterExportDisabled;

  return (
    <div className={cn("relative", className)} data-testid="export-menu">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        disabled={triggerDisabled}
        className="rounded px-2 py-1 text-xs text-ink-muted hover:text-ink disabled:opacity-50"
        aria-expanded={open}
        aria-haspopup="menu"
        data-testid="export-menu-trigger"
      >
        Esporta
      </button>
      {open && (
        <div
          role="menu"
          className="absolute right-0 z-20 mt-1 min-w-[11rem] rounded-md border border-border bg-surface py-1 shadow-lg"
          data-testid="export-menu-panel"
        >
          <button
            type="button"
            role="menuitem"
            disabled={chapterItemDisabled}
            onClick={() => void handleExportMarkdown()}
            className="block w-full px-3 py-1.5 text-left text-xs text-ink hover:bg-surface-muted disabled:opacity-50"
            data-testid="chapter-export-md"
          >
            Scarica capitolo .md
          </button>
          <button
            type="button"
            role="menuitem"
            disabled={busy}
            onClick={() => void handleExportManuscript()}
            className="block w-full px-3 py-1.5 text-left text-xs text-ink hover:bg-surface-muted disabled:opacity-50"
            data-testid="manuscript-export-md"
          >
            Scarica manoscritto .md
          </button>
        </div>
      )}
    </div>
  );
}
