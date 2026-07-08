"use client";

import { useCallback, useState } from "react";

import { cn } from "@/lib/cn";
import { chapterClient } from "@/lib/chapterClient";

export type ExportMenuProps = {
  chapterId: string | null | undefined;
  disabled?: boolean;
  onError?: () => void;
  className?: string;
};

/** Chapter export actions (M7 P-EXPORT-MIN). */
export function ExportMenu({ chapterId, disabled = false, onError, className }: ExportMenuProps) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);

  const handleExportMarkdown = useCallback(async () => {
    if (!chapterId) return;
    setBusy(true);
    setOpen(false);
    try {
      const blob = await chapterClient.exportMarkdown(chapterId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${chapterId}.md`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      onError?.();
    } finally {
      setBusy(false);
    }
  }, [chapterId, onError]);

  const inactive = disabled || !chapterId || busy;

  return (
    <div className={cn("relative", className)} data-testid="export-menu">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        disabled={inactive}
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
          className="absolute right-0 z-20 mt-1 min-w-[9rem] rounded-md border border-border bg-surface py-1 shadow-lg"
          data-testid="export-menu-panel"
        >
          <button
            type="button"
            role="menuitem"
            disabled={busy}
            onClick={() => void handleExportMarkdown()}
            className="block w-full px-3 py-1.5 text-left text-xs text-ink hover:bg-surface-muted disabled:opacity-50"
            data-testid="chapter-export-md"
          >
            Scarica .md
          </button>
        </div>
      )}
    </div>
  );
}
