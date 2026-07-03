import { cn } from "@/lib/cn";
import { chapterTitle } from "@/components/writing/writingStub";

export type WritingEditorShellProps = {
  chapterId?: string;
  className?: string;
};

/**
 * Markdown editor placeholder — center panel (PX-2 delivers full editor).
 * Layer: Business (Product Plane)
 */
export function WritingEditorShell({
  chapterId,
  className,
}: WritingEditorShellProps) {
  const title = chapterId ? chapterTitle(chapterId) : "Seleziona un capitolo";

  return (
    <section
      aria-label="Editor Markdown"
      className={cn("flex h-full flex-col", className)}
    >
      <header className="flex items-center justify-between border-b border-border px-4 py-3">
        <div className="min-w-0">
          <p className="text-xs font-medium uppercase tracking-wide text-ink-subtle">
            Editor
          </p>
          <h2 className="truncate text-sm font-semibold text-ink">{title}</h2>
        </div>
        <span className="shrink-0 rounded-full border border-border bg-surface-muted px-2 py-0.5 text-xs text-ink-muted">
          PX-2
        </span>
      </header>
      <div className="flex flex-1 flex-col p-4">
        <div
          className="flex flex-1 flex-col rounded-md border border-dashed border-border bg-surface-muted p-6"
          data-testid="writing-editor-placeholder"
        >
          {chapterId ? (
            <>
              <p className="text-sm text-ink-muted">
                L&apos;editor Markdown con autosave e cronologia versioni arriva in
                PX-2.
              </p>
              <pre className="mt-4 flex-1 overflow-auto rounded-md border border-border bg-surface p-4 font-mono text-xs leading-relaxed text-ink-muted">
                {`# ${title}\n\n<!-- Contenuto capitolo ${chapterId} — placeholder -->`}
              </pre>
            </>
          ) : (
            <p className="text-sm text-ink-muted">
              Scegli un capitolo dall&apos;outline per aprire l&apos;area di scrittura.
            </p>
          )}
        </div>
      </div>
    </section>
  );
}
