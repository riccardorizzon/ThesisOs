"use client";

import { cn } from "@/lib/cn";
import { StatusBadge } from "@/components/ui/StatusBadge";
import type { ManuscriptOutline } from "@/lib/manuscriptToc";

export type ManuscriptTocProps = {
  outline: ManuscriptOutline;
  activeChapterId: string | null;
  onSelectChapter: (chapterId: string) => void;
  className?: string;
};

/** Indice gerarchico — Cap. N con sottocapitoli §N.x e gruppo Altri. */
export function ManuscriptToc({
  outline,
  activeChapterId,
  onSelectChapter,
  className,
}: ManuscriptTocProps) {
  const { parts, others } = outline;
  const sectionCount = parts.reduce((sum, part) => sum + part.sections.length, 0);
  const isEmpty = parts.length === 0 && others.length === 0;

  return (
    <nav
      aria-label="Indice manoscritto"
      data-testid="manuscript-toc"
      className={cn("flex h-full flex-col border-r border-border bg-surface", className)}
    >
      <header className="border-b border-border px-3 py-3">
        <h2 className="text-sm font-semibold text-ink">Indice</h2>
        <p className="mt-1 text-xs text-ink-muted">Capitoli e sottocapitoli della tesi</p>
        {!isEmpty ? (
          <p className="mt-1 text-xs text-ink-subtle">
            {parts.length} {parts.length === 1 ? "capitolo" : "capitoli"}
            {sectionCount > 0
              ? ` · ${sectionCount} ${sectionCount === 1 ? "sottocapitolo" : "sottocapitoli"}`
              : ""}
            {others.length > 0
              ? ` · ${others.length} ${others.length === 1 ? "altro" : "altri"}`
              : ""}
          </p>
        ) : null}
      </header>

      {isEmpty ? (
        <div className="flex-1 p-4 text-sm text-ink-muted">
          <p>Nessun capitolo strutturato trovato.</p>
          <p className="mt-2 text-xs">
            Usa titoli come <span className="font-mono">Cap. 3 — …</span> o{" "}
            <span className="font-mono">§3.6 …</span> in Writing.
          </p>
        </div>
      ) : (
        <ol className="flex-1 list-none overflow-y-auto p-2">
          {parts.map((part) => {
            const partActive = part.chapterId === activeChapterId;
            return (
              <li key={part.number} className="mb-3">
                {part.chapterId ? (
                  <button
                    type="button"
                    aria-current={partActive ? "page" : undefined}
                    onClick={() => onSelectChapter(part.chapterId!)}
                    className={cn(
                      "flex w-full items-start gap-2 rounded-md px-2 py-1.5 text-left text-sm transition-colors",
                      "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent",
                      partActive
                        ? "bg-accent-subtle font-medium text-accent"
                        : "font-medium text-ink hover:bg-surface-muted"
                    )}
                  >
                    <span className="shrink-0 tabular-nums text-ink-muted">{part.number}.</span>
                    <span className="min-w-0 flex-1 leading-snug">{part.title}</span>
                    {part.status ? <StatusBadge status={part.status} /> : null}
                  </button>
                ) : (
                  <div className="flex items-start gap-2 px-2 py-1.5 text-sm font-medium text-ink">
                    <span className="shrink-0 tabular-nums text-ink-muted">{part.number}.</span>
                    <span className="min-w-0 flex-1 leading-snug">{part.title}</span>
                  </div>
                )}

                {part.sections.length > 0 ? (
                  <ol className="mt-0.5 list-none space-y-0.5 border-l border-border ml-4">
                    {part.sections.map((section) => {
                      const sectionActive = section.id === activeChapterId;
                      return (
                        <li key={section.id}>
                          <button
                            type="button"
                            aria-current={sectionActive ? "page" : undefined}
                            onClick={() => onSelectChapter(section.id)}
                            className={cn(
                              "flex w-full items-start gap-2 py-1 pl-3 pr-2 text-left text-xs leading-snug transition-colors",
                              "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent",
                              sectionActive
                                ? "font-medium text-accent"
                                : "text-ink-muted hover:text-ink"
                            )}
                          >
                            <span className="shrink-0 tabular-nums text-ink-subtle">
                              {section.number}
                            </span>
                            <span className="min-w-0 flex-1">{section.label}</span>
                            <StatusBadge status={section.status} className="scale-90" />
                          </button>
                        </li>
                      );
                    })}
                  </ol>
                ) : null}
              </li>
            );
          })}

          {others.length > 0 ? (
            <li className="mb-3" data-testid="manuscript-toc-others">
              <div className="px-2 py-1.5 text-sm font-medium text-ink">Altri</div>
              <ol className="mt-0.5 list-none space-y-0.5 border-l border-border ml-4">
                {others.map((other) => {
                  const otherActive = other.id === activeChapterId;
                  return (
                    <li key={other.id}>
                      <button
                        type="button"
                        aria-current={otherActive ? "page" : undefined}
                        onClick={() => onSelectChapter(other.id)}
                        className={cn(
                          "flex w-full items-start gap-2 py-1 pl-3 pr-2 text-left text-xs leading-snug transition-colors",
                          "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent",
                          otherActive
                            ? "font-medium text-accent"
                            : "text-ink-muted hover:text-ink"
                        )}
                      >
                        <span className="min-w-0 flex-1">{other.label}</span>
                        <StatusBadge status={other.status} className="scale-90" />
                      </button>
                    </li>
                  );
                })}
              </ol>
            </li>
          ) : null}
        </ol>
      )}
    </nav>
  );
}
