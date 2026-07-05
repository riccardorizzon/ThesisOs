"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { cn } from "@/lib/cn";
import {
  corpusClient,
  LINKED_SOURCES_CHANGED,
  type CorpusSource,
} from "@/lib/corpusClient";

export type LinkedSourcesFooterProps = {
  chapterId?: string;
  className?: string;
};

/**
 * Collapsible linked-sources strip below Writing panels (UI spec §5.5).
 * Layer: Business (Product Plane)
 */
export function LinkedSourcesFooter({ chapterId, className }: LinkedSourcesFooterProps) {
  const [expanded, setExpanded] = useState(false);
  const [linked, setLinked] = useState<CorpusSource[]>([]);

  const refresh = useCallback(() => {
    if (!chapterId) {
      setLinked([]);
      return;
    }
    setLinked(corpusClient.getLinkedToChapter(chapterId));
  }, [chapterId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    const onChange = () => refresh();
    window.addEventListener(LINKED_SOURCES_CHANGED, onChange);
    return () => window.removeEventListener(LINKED_SOURCES_CHANGED, onChange);
  }, [refresh]);

  if (!chapterId) return null;

  const count = linked.length;

  return (
    <footer
      aria-label="Fonti collegate"
      className={cn(
        "rounded-lg border border-border bg-surface-muted",
        className
      )}
      data-testid="linked-sources-footer"
    >
      <button
        type="button"
        onClick={() => setExpanded((e) => !e)}
        className="flex w-full items-center justify-between px-4 py-2 text-left cursor-pointer"
        aria-expanded={expanded}
        data-testid="linked-sources-toggle"
      >
        <span className="text-xs font-medium text-ink">
          Fonti collegate ({count})
        </span>
        <span className="text-xs text-ink-subtle" aria-hidden>
          {expanded ? "▾" : "▸"}
        </span>
      </button>

      {expanded && (
        <div className="border-t border-border px-4 py-3">
          {count > 0 ? (
            <ul className="flex flex-wrap gap-2">
              {linked.map((source) => (
                <li key={source.id}>
                  <Link
                    href={`/sources/${source.id}?chapter=${chapterId}`}
                    className="inline-flex rounded-full border border-border bg-surface px-2.5 py-1 text-xs text-ink hover:border-accent hover:text-accent cursor-pointer"
                  >
                    {source.title}
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-ink-muted">
              Nessuna fonte collegata.{" "}
              <span className="text-accent">Cita fonte</span> (⌘⇧C) per aggiungerne una.
            </p>
          )}
        </div>
      )}
    </footer>
  );
}
