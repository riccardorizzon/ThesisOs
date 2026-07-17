"use client";

import { useRouter } from "next/navigation";
import { useCallback, useRef, useState } from "react";

import { cn } from "@/lib/cn";
import { getActiveProjectId } from "@/lib/projectPrefs";
import { chapterClient, type Chapter } from "@/lib/chapterClient";

export const DEFAULT_CHAPTER_TITLE = "Introduzione";

export type CreateChapterButtonProps = {
  variant?: "primary" | "icon";
  defaultTitle?: string;
  onCreated?: (chapter: Chapter) => void;
  className?: string;
  testId?: string;
  disabled?: boolean;
};

export function CreateChapterButton({
  variant = "primary",
  defaultTitle = DEFAULT_CHAPTER_TITLE,
  onCreated,
  className,
  testId = "writing-create-chapter-cta",
  disabled = false,
}: CreateChapterButtonProps) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState(defaultTitle);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const resetForm = useCallback(() => {
    setTitle(defaultTitle);
    setError(null);
    setOpen(false);
  }, [defaultTitle]);

  const handleOpen = () => {
    setTitle(defaultTitle);
    setError(null);
    setOpen(true);
    requestAnimationFrame(() => inputRef.current?.focus());
  };

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const trimmed = title.trim();
    if (!trimmed) {
      setError("Inserisci un titolo per il capitolo.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const chapter = await chapterClient.create({ project_id: getActiveProjectId(), title: trimmed });
      onCreated?.(chapter);
      resetForm();
      router.push(`/writing/${chapter.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Creazione capitolo fallita");
    } finally {
      setBusy(false);
    }
  }

  if (open) {
    return (
      <form
        onSubmit={(event) => void handleSubmit(event)}
        className={cn(
          variant === "icon" ? "border-b border-border px-3 py-2" : "rounded-lg border border-border bg-surface-muted p-4",
          className
        )}
        data-testid="writing-create-chapter-form"
      >
        <label htmlFor="chapter-title" className="block text-sm font-medium text-ink">
          Titolo capitolo
        </label>
        <input
          id="chapter-title"
          ref={inputRef}
          type="text"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          disabled={busy}
          className="mt-1 w-full rounded-md border border-border bg-surface px-3 py-2 text-sm text-ink"
          data-testid="writing-create-chapter-title"
        />
        {error ? (
          <p className="mt-2 text-sm text-warning" role="alert">
            {error}
          </p>
        ) : null}
        <div className="mt-3 flex flex-wrap gap-2">
          <button
            type="submit"
            disabled={busy}
            className="rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-white hover:bg-accent/90 disabled:opacity-50 cursor-pointer"
            data-testid="writing-create-chapter-submit"
          >
            {busy ? "Creazione…" : "Crea e scrivi"}
          </button>
          <button
            type="button"
            disabled={busy}
            onClick={resetForm}
            className="rounded-md border border-border bg-surface px-3 py-1.5 text-sm font-medium text-ink hover:bg-surface-muted cursor-pointer"
            data-testid="writing-create-chapter-cancel"
          >
            Annulla
          </button>
        </div>
      </form>
    );
  }

  if (variant === "icon") {
    return (
      <button
        type="button"
        onClick={handleOpen}
        disabled={disabled}
        aria-label="Crea capitolo"
        title="Crea capitolo"
        className={cn(
          "inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-md border border-border",
          "bg-surface text-ink-muted transition-colors hover:border-accent hover:bg-accent-subtle hover:text-accent",
          "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent cursor-pointer",
          disabled && "pointer-events-none opacity-50",
          className
        )}
        data-testid={testId}
      >
        <span aria-hidden="true">+</span>
      </button>
    );
  }

  return (
    <button
      type="button"
      onClick={handleOpen}
      disabled={disabled}
      className={cn(
        "inline-flex rounded-md bg-accent px-4 py-2 text-sm font-medium text-white",
        "transition-colors hover:bg-accent/90",
        "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent cursor-pointer",
        disabled && "opacity-50",
        className
      )}
      data-testid={testId}
    >
      Crea capitolo
    </button>
  );
}
