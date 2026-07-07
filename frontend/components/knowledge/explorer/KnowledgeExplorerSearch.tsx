"use client";

import { useCallback, useState } from "react";

import { searchKnowledge } from "@/lib/knowledgeClient";
import type { KnowledgeObjectEnvelope } from "@/lib/knowledgeTypes";

export type KnowledgeExplorerSearchProps = {
  onResults: (results: KnowledgeObjectEnvelope[] | null) => void;
  className?: string;
};

export function KnowledgeExplorerSearch({
  onResults,
  className,
}: KnowledgeExplorerSearchProps) {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runSearch = useCallback(
    async (value: string) => {
      const trimmed = value.trim();
      if (!trimmed) {
        setError(null);
        onResults(null);
        return;
      }
      setLoading(true);
      try {
        const res = await searchKnowledge(trimmed);
        setError(null);
        onResults(res.results);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Ricerca non disponibile.";
        setError(message);
        onResults(null);
      } finally {
        setLoading(false);
      }
    },
    [onResults]
  );

  return (
    <div className={className}>
      <label htmlFor="knowledge-search" className="sr-only">
        Cerca concetti
      </label>
      <input
        id="knowledge-search"
        type="search"
        placeholder="Cerca concetti…"
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          void runSearch(e.target.value);
        }}
        className="w-full rounded-md border border-border bg-surface px-3 py-2 text-sm text-ink placeholder:text-ink-muted focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
        aria-busy={loading}
      />
      {error != null && (
        <p
          className="mt-2 text-sm text-red-700"
          role="alert"
          data-testid="knowledge-search-error"
        >
          {error}
        </p>
      )}
    </div>
  );
}
