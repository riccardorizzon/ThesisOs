"use client";

import { useState } from "react";
import { exportBibliography } from "@/lib/sourcesClient";
import { getActiveProjectId } from "@/lib/projectPrefs";

/** Bibliography export actions (PX6-EWO-005/006). */
export function BibliographyExportBar() {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleExport = async () => {
    setBusy(true);
    setError(null);
    try {
      const blob = await exportBibliography(getActiveProjectId());
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${getActiveProjectId()}-bibliografia.bib`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Export fallito");
    } finally {
      setBusy(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div
      className="mb-6 flex flex-wrap items-center gap-3 rounded-md border border-border bg-surface-muted p-3 print:hidden"
      data-testid="bibliography-export-bar"
    >
      <span className="text-sm font-medium text-ink">Bibliografia</span>
      <button
        type="button"
        disabled={busy}
        onClick={() => void handleExport()}
        className="rounded-md border border-border bg-surface px-3 py-1.5 text-xs font-medium text-ink cursor-pointer disabled:opacity-50"
      >
        Esporta BibTeX
      </button>
      <button
        type="button"
        onClick={handlePrint}
        className="rounded-md border border-border bg-surface px-3 py-1.5 text-xs font-medium text-ink cursor-pointer"
      >
        Stampa
      </button>
      {error && <p className="text-xs text-warning">{error}</p>}
    </div>
  );
}
