"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { cn } from "@/lib/cn";
import {
  canCiteSource,
  dispatchInsertCitation,
  EXCLUDED_CITE_BLOCKED_MESSAGE,
  formatCitationMarker,
} from "@/lib/citationInsert";
import {
  corpusClient,
  type CorpusSource,
} from "@/lib/corpusClient";
import {
  sourceStatusMeta,
  type SourceStatus,
} from "@/lib/libraryTypes";

export type SourceReaderProps = {
  source: CorpusSource;
  variant?: "full" | "peek";
  resultIds?: string[];
  chapterId?: string;
  onNavigate?: (sourceId: string) => void;
  onCite?: (source: CorpusSource, quote?: string) => void;
  onDismiss?: () => void;
  className?: string;
};

const STATUS_BADGE: Record<SourceStatus, string> = {
  candidata: "bg-accent-subtle text-accent",
  approvata: "bg-success/10 text-success",
  esclusa: "bg-danger/10 text-danger",
};

function SourceStatusBadge({ status }: { status: SourceStatus }) {
  return (
    <span
      className={cn(
        "inline-flex rounded-full px-2 py-0.5 text-xs font-medium",
        STATUS_BADGE[status]
      )}
      data-testid="source-status-badge"
    >
      {sourceStatusMeta(status)}
    </span>
  );
}

/**
 * Source reader — full page or peek (Fonte tab). UI spec §6.5.
 */
export function SourceReader({
  source,
  variant = "full",
  resultIds,
  chapterId,
  onNavigate,
  onCite,
  onDismiss,
  className,
}: SourceReaderProps) {
  const bodyRef = useRef<HTMLElement>(null);
  const [selectedQuote, setSelectedQuote] = useState("");
  const [citeBlockedMsg, setCiteBlockedMsg] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const isExcluded = !canCiteSource(source.status);
  const conceptTags = source.relatedConcepts ?? source.relatedConceptIds.map((id) => ({
    id,
    title: id,
  }));

  const navIndex = resultIds?.indexOf(source.id) ?? -1;
  const prevId = navIndex > 0 ? resultIds?.[navIndex - 1] : undefined;
  const nextId =
    resultIds != null && navIndex >= 0 && navIndex < resultIds.length - 1
      ? resultIds[navIndex + 1]
      : undefined;

  useEffect(() => {
    corpusClient.recordRecent(source.id);
  }, [source.id]);

  useEffect(() => {
    if (variant !== "peek" || !onDismiss) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onDismiss();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [variant, onDismiss]);

  const handleSelection = useCallback(() => {
    const sel = window.getSelection()?.toString().trim() ?? "";
    setSelectedQuote(sel);
  }, []);

  const handleCopyQuote = useCallback(async () => {
    const text = selectedQuote || source.body.slice(0, 200);
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      /* clipboard unavailable in test env */
    }
  }, [selectedQuote, source.body]);

  const handleCite = useCallback(() => {
    if (isExcluded) {
      setCiteBlockedMsg(EXCLUDED_CITE_BLOCKED_MESSAGE);
      return;
    }
    setCiteBlockedMsg(null);
    const marker = formatCitationMarker(source);
    if (onCite) {
      onCite(source, selectedQuote || undefined);
    } else {
      dispatchInsertCitation({
        marker,
        sourceId: source.id,
        quote: selectedQuote || undefined,
      });
    }
  }, [isExcluded, onCite, selectedQuote, source]);

  const handleInsertCitation = useCallback(() => {
    handleCite();
  }, [handleCite]);

  const isPeek = variant === "peek";

  return (
    <article
      className={cn(
        isPeek ? "flex h-full flex-col" : "mx-auto max-w-content",
        className
      )}
      data-testid={`source-reader-${variant}`}
      aria-label={`Lettore fonte — ${source.title}`}
    >
      <header
        className={cn(
          "shrink-0 border-b border-border",
          isPeek ? "px-3 py-3" : "mb-6 rounded-lg border bg-surface p-6 shadow-sm"
        )}
      >
        <div className="flex flex-wrap items-center gap-2">
          <SourceStatusBadge status={source.status} />
          {isExcluded && (
            <span
              className="inline-flex items-center gap-1 rounded-full bg-danger/10 px-2 py-0.5 text-xs font-medium text-danger"
              data-testid="source-excluded-ban"
            >
              Esclusa
            </span>
          )}
        </div>
        <h1
          className={cn(
            "mt-2 font-semibold tracking-tight text-ink",
            isPeek ? "text-base" : "text-2xl"
          )}
        >
          {source.title}
        </h1>
        {source.subtitle != null && (
          <p className="mt-1 text-sm text-ink-muted">{source.subtitle}</p>
        )}
        <div className="mt-2 flex flex-wrap gap-2 text-xs text-ink-subtle">
          {source.year != null && <span>{source.year}</span>}
          {source.meta != null && <span>{source.meta}</span>}
        </div>
        {conceptTags.length > 0 && (
          <ul className="mt-3 flex flex-wrap gap-1.5" aria-label="Tag concetti">
            {conceptTags.map((c) =>
              c ? (
                <li key={c.id}>
                  <span className="rounded-full border border-border bg-surface-muted px-2 py-0.5 text-xs text-ink-muted">
                    {c.title}
                  </span>
                </li>
              ) : null
            )}
          </ul>
        )}
        {isExcluded && source.exclusionReason != null && (
          <p
            className="mt-3 rounded-md border border-danger/20 bg-danger/5 px-3 py-2 text-sm text-danger"
            data-testid="source-exclusion-reason"
          >
            {source.exclusionReason}
          </p>
        )}
      </header>

      <section
        ref={bodyRef}
        className={cn(
          "min-h-0 flex-1 overflow-y-auto text-sm leading-relaxed text-ink",
          isPeek ? "px-3 py-3" : "mt-4"
        )}
        onMouseUp={handleSelection}
        data-testid="source-reader-body"
      >
        {source.body.split("\n\n").map((para, i) => (
          <p key={i} className="mb-4 last:mb-0">
            {para}
          </p>
        ))}
      </section>

      <footer
        className={cn(
          "shrink-0 border-t border-border",
          isPeek ? "px-3 py-2" : "mt-6 rounded-lg border bg-surface-muted p-4"
        )}
      >
        {selectedQuote && (
          <blockquote className="mb-3 border-l-2 border-accent pl-3 text-xs italic text-ink-muted">
            {selectedQuote}
          </blockquote>
        )}

        {citeBlockedMsg && (
          <p
            className="mb-3 text-sm text-danger"
            role="alert"
            data-testid="cite-blocked-message"
          >
            {citeBlockedMsg}
          </p>
        )}

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => void handleCopyQuote()}
            className="rounded-md border border-border px-3 py-1.5 text-xs font-medium text-ink-muted hover:bg-surface-muted cursor-pointer"
            data-testid="copy-quote-btn"
          >
            {copied ? "Copiato" : "Copia estratto"}
          </button>
          <button
            type="button"
            onClick={handleInsertCitation}
            className={cn(
              "rounded-md px-3 py-1.5 text-xs font-medium cursor-pointer",
              isExcluded
                ? "border border-danger/30 text-danger hover:bg-danger/5"
                : "bg-accent text-white hover:bg-accent-muted"
            )}
            data-testid="insert-citation-btn"
            aria-disabled={isExcluded}
          >
            Inserisci citazione
          </button>
          {chapterId && !corpusClient.isLinkedToChapter(chapterId, source.id) && (
            <button
              type="button"
              onClick={() => corpusClient.linkToChapter(chapterId, source.id)}
              className="rounded-md border border-border px-3 py-1.5 text-xs font-medium text-ink hover:bg-surface-muted cursor-pointer"
            >
              Collega
            </button>
          )}
          {!isPeek && chapterId && (
            <Link
              href={`/writing/${chapterId}`}
              className="rounded-md border border-accent px-3 py-1.5 text-xs font-medium text-accent hover:bg-accent-subtle cursor-pointer"
            >
              Apri in Writing
            </Link>
          )}
          {(prevId || nextId) && onNavigate && (
            <div className="ml-auto flex gap-2">
              <button
                type="button"
                disabled={!prevId}
                onClick={() => prevId && onNavigate(prevId)}
                className="rounded-md border border-border px-2 py-1 text-xs disabled:opacity-40 cursor-pointer"
                aria-label="Fonte precedente"
              >
                ← Prec
              </button>
              <button
                type="button"
                disabled={!nextId}
                onClick={() => nextId && onNavigate(nextId)}
                className="rounded-md border border-border px-2 py-1 text-xs disabled:opacity-40 cursor-pointer"
                aria-label="Fonte successiva"
              >
                Succ →
              </button>
            </div>
          )}
          {isPeek && onDismiss && (
            <button
              type="button"
              onClick={onDismiss}
              className="ml-auto rounded-md border border-border px-3 py-1.5 text-xs text-ink-muted hover:bg-surface-muted cursor-pointer"
              data-testid="peek-dismiss-btn"
            >
              Chiudi
            </button>
          )}
        </div>
      </footer>
    </article>
  );
}
