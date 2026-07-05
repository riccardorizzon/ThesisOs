"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { cn } from "@/lib/cn";
import { canCiteSource, EXCLUDED_CITE_BLOCKED_MESSAGE } from "@/lib/citationInsert";
import { corpusClient, type CorpusSource } from "@/lib/corpusClient";

export type SourcePickerTab = "recenti" | "collegate" | "risultati";

export type SourcePickerProps = {
  open: boolean;
  onClose: () => void;
  chapterId?: string;
  onSelectSource: (source: CorpusSource) => void;
  className?: string;
};

const DEBOUNCE_MS = 200;

function SourceRow({
  source,
  onSelect,
}: {
  source: CorpusSource;
  onSelect: (source: CorpusSource) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onSelect(source)}
      className="flex w-full flex-col rounded-md px-3 py-2 text-left hover:bg-surface-muted cursor-pointer"
      data-testid={`source-picker-row-${source.id}`}
    >
      <span className="text-sm font-medium text-ink">{source.title}</span>
      <span className="text-xs text-ink-muted">
        {[source.subtitle, source.year ?? source.meta?.match(/\d{4}/)?.[0]]
          .filter(Boolean)
          .join(" · ")}
      </span>
    </button>
  );
}

/**
 * Source picker modal — Recenti / Collegate / Risultati (UI spec §6.4).
 */
export function SourcePicker({
  open,
  onClose,
  chapterId,
  onSelectSource,
  className,
}: SourcePickerProps) {
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [searching, setSearching] = useState(false);
  const [tab, setTab] = useState<SourcePickerTab>("recenti");
  const [remoteResults, setRemoteResults] = useState<CorpusSource[]>([]);
  const [blockedMsg, setBlockedMsg] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    const t = window.setTimeout(() => setDebouncedQuery(query), DEBOUNCE_MS);
    return () => window.clearTimeout(t);
  }, [query, open]);

  useEffect(() => {
    if (!open) {
      setQuery("");
      setDebouncedQuery("");
      setBlockedMsg(null);
      setTab("recenti");
    }
  }, [open]);

  useEffect(() => {
    if (!debouncedQuery.trim()) {
      setRemoteResults([]);
      setSearching(false);
      return;
    }
    let cancelled = false;
    setSearching(true);
    void corpusClient.searchRemote(debouncedQuery).then((results) => {
      if (!cancelled) {
        setRemoteResults(results);
        setSearching(false);
      }
    });
    return () => {
      cancelled = true;
    };
  }, [debouncedQuery]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  const recentSources = useMemo(() => corpusClient.getRecent(), [open]);
  const linkedSources = useMemo(
    () => (chapterId ? corpusClient.getLinkedToChapter(chapterId) : []),
    [chapterId, open]
  );

  const resultSources = useMemo(() => {
    if (debouncedQuery.trim()) {
      return remoteResults.length > 0
        ? remoteResults
        : corpusClient.search(debouncedQuery);
    }
    return corpusClient.search("");
  }, [debouncedQuery, remoteResults]);

  const activeList = useMemo(() => {
    switch (tab) {
      case "recenti":
        return recentSources;
      case "collegate":
        return linkedSources;
      case "risultati":
        return resultSources;
    }
  }, [tab, recentSources, linkedSources, resultSources]);

  const handleSelect = useCallback(
    (source: CorpusSource) => {
      if (!canCiteSource(source.status)) {
        setBlockedMsg(EXCLUDED_CITE_BLOCKED_MESSAGE);
        return;
      }
      setBlockedMsg(null);
      corpusClient.recordRecent(source.id);
      onSelectSource(source);
    },
    [onSelectSource]
  );

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-ink/40 p-4 pt-[10vh]"
      role="dialog"
      aria-modal="true"
      aria-labelledby="source-picker-title"
      data-testid="source-picker-modal"
      onClick={onClose}
    >
      <div
        className={cn(
          "flex w-full max-w-xl max-h-[80vh] flex-col overflow-hidden rounded-lg border border-border bg-surface shadow-md",
          className
        )}
        onClick={(e) => e.stopPropagation()}
      >
        <header className="sticky top-0 z-10 border-b border-border bg-surface px-4 py-3">
          <div className="flex items-center justify-between gap-2">
            <h2 id="source-picker-title" className="text-base font-semibold text-ink">
              Cita fonte
            </h2>
            <button
              type="button"
              onClick={onClose}
              className="rounded px-2 py-1 text-sm text-ink-muted hover:bg-surface-muted cursor-pointer"
              aria-label="Chiudi"
            >
              ✕
            </button>
          </div>
          <div className="relative mt-3">
            <input
              type="search"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                if (e.target.value.trim()) setTab("risultati");
              }}
              placeholder="Cerca per titolo, autore, anno…"
              className="w-full rounded-md border border-border bg-surface px-3 py-2 pr-8 text-sm text-ink placeholder:text-ink-subtle focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
              data-testid="source-picker-search"
              aria-label="Cerca fonti"
            />
            {searching && (
              <span
                className="absolute right-2 top-1/2 -translate-y-1/2 inline-block h-4 w-4 animate-spin rounded-full border-2 border-accent border-t-transparent"
                aria-hidden
                data-testid="source-picker-spinner"
              />
            )}
          </div>
        </header>

        <div
          role="tablist"
          aria-label="Colonne fonti"
          className="flex border-b border-border px-2"
        >
          {(
            [
              ["recenti", "Recenti"],
              ["collegate", "Collegate"],
              ["risultati", "Risultati"],
            ] as const
          ).map(([value, label]) => (
            <button
              key={value}
              type="button"
              role="tab"
              aria-selected={tab === value}
              onClick={() => setTab(value)}
              className={cn(
                "px-3 py-2 text-xs font-medium cursor-pointer",
                tab === value
                  ? "border-b-2 border-accent text-accent"
                  : "text-ink-muted hover:text-ink"
              )}
            >
              {label}
              {value === "collegate" && linkedSources.length > 0 && (
                <span className="ml-1 text-ink-subtle">({linkedSources.length})</span>
              )}
            </button>
          ))}
        </div>

        {blockedMsg && (
          <p
            className="mx-4 mt-3 rounded-md border border-danger/20 bg-danger/5 px-3 py-2 text-sm text-danger"
            role="alert"
            data-testid="picker-cite-blocked"
          >
            {blockedMsg}
          </p>
        )}

        <div
          role="tabpanel"
          className="min-h-0 flex-1 overflow-y-auto px-2 py-2"
          data-testid="source-picker-list"
        >
          {activeList.length > 0 ? (
            activeList.map((source) => (
              <SourceRow key={source.id} source={source} onSelect={handleSelect} />
            ))
          ) : (
            <p className="px-3 py-6 text-center text-sm text-ink-muted">
              {tab === "collegate"
                ? "Nessuna fonte collegata a questo capitolo."
                : tab === "recenti"
                  ? "Nessuna fonte usata di recente."
                  : "Nessun risultato — prova un'altra ricerca."}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
