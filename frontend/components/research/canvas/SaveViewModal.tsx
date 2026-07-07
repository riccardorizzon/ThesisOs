"use client";

import { useState } from "react";

export type SaveViewModalProps = {
  open: boolean;
  onClose: () => void;
  onSave: (payload: { name: string; description?: string; includeSelection: boolean }) => void;
};

/**
 * Saved view naming modal (PX5-EWO-010).
 */
export function SaveViewModal({ open, onClose, onSave }: SaveViewModalProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [includeSelection, setIncludeSelection] = useState(false);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40 p-4"
      data-testid="canvas-save-view-modal"
      role="dialog"
      aria-label="Salva vista"
    >
      <form
        className="w-full max-w-md rounded-lg border border-border bg-surface p-5 shadow-lg"
        onSubmit={(event) => {
          event.preventDefault();
          if (name.trim().length === 0) return;
          onSave({
            name: name.trim(),
            description: description.trim() || undefined,
            includeSelection,
          });
          setName("");
          setDescription("");
          setIncludeSelection(false);
          onClose();
        }}
      >
        <h2 className="text-base font-semibold text-ink">Salva vista</h2>
        <label className="mt-4 block text-sm text-ink">
          Nome
          <input
            value={name}
            onChange={(event) => setName(event.target.value)}
            maxLength={64}
            required
            className="mt-1 w-full rounded-md border border-border bg-bg px-3 py-2 text-sm"
            data-testid="save-view-name"
          />
        </label>
        <label className="mt-3 block text-sm text-ink">
          Descrizione
          <textarea
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            className="mt-1 w-full rounded-md border border-border bg-bg px-3 py-2 text-sm"
            rows={2}
          />
        </label>
        <label className="mt-3 flex items-center gap-2 text-sm text-ink-muted">
          <input
            type="checkbox"
            checked={includeSelection}
            onChange={(event) => setIncludeSelection(event.target.checked)}
            data-testid="save-view-include-selection"
          />
          Includi selezione
        </label>
        <div className="mt-4 flex justify-end gap-2">
          <button
            type="button"
            className="rounded-md border border-border px-3 py-2 text-sm cursor-pointer"
            onClick={onClose}
          >
            Annulla
          </button>
          <button
            type="submit"
            className="rounded-md bg-accent px-3 py-2 text-sm font-medium text-on-accent cursor-pointer"
            data-testid="save-view-submit"
          >
            Salva
          </button>
        </div>
      </form>
    </div>
  );
}
