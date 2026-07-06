"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { cn } from "@/lib/cn";
import {
  corpusClient,
  LINKED_SOURCES_CHANGED,
  type CorpusSource,
} from "@/lib/corpusClient";
import { getSource } from "@/lib/sourcesClient";
import type { RelatedConceptRef } from "@/lib/sourcesTypes";

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
  const [relatedConcepts, setRelatedConcepts] = useState<RelatedConceptRef[]>([]);

  const refresh = useCallback(() => {
    if (!chapterId) {
      setLinked([]);
      setRelatedConcepts([]);
      return;
    }
    setLinked(corpusClient.getLinkedToChapter(chapterId));
  }, [chapterId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    if (linked.length === 0) {
      setRelatedConcepts([]);
      return;
    }
    let cancelled = false;
    Promise.all(linked.slice(0, 5).map((s) => getSource(s.id).catch(() => null)))
      .then((results) => {
        if (cancelled) return;
        const seen = new Set<string>();
        const merged: RelatedConceptRef[] = [];
        for (const item of results) {
          if (!item) continue;
          for (const concept of item.related_concepts) {
            if (seen.has(concept.slug)) continue;
            seen.add(concept.slug);
            merged.push(concept);
          }
        }
        setRelatedConcepts(merged);
      })
      .catch(() => {
        if (!cancelled) setRelatedConcepts([]);
      });
    return () => {
      cancelled = true;
    };
  }, [linked]);

  const conceptLinks = useMemo(() => relatedConcepts.slice(0, 8), [relatedConcepts]);

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
          {conceptLinks.length > 0 && (
            <div className="mt-3 border-t border-border pt-3">
              <p className="mb-2 text-xs font-medium text-ink-subtle">
                Concetti collegati
              </p>
              <ul className="flex flex-wrap gap-2">
                {conceptLinks.map((concept) => (
                  <li key={concept.slug}>
                    <Link
                      href={`/knowledge/${concept.slug}`}
                      className="inline-flex rounded-full border border-accent/30 bg-accent-subtle/40 px-2.5 py-1 text-xs text-accent hover:bg-accent/10"
                    >
                      {concept.title}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </footer>
  );
}
