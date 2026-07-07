"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { cn } from "@/lib/cn";
import { chapterClient, type Chapter } from "@/lib/chapterClient";
import { proposalClient } from "@/lib/proposalClient";
import type { WritingProposal } from "@/lib/proposalQueue";
import {
  applyProposalToContent,
  computeParagraphDiff,
  mergeAcceptedHunks,
  selectableHunks,
  type ParagraphHunk,
} from "@/lib/reviewDiff";

export type ReviewCompareProps = {
  chapterId: string;
  proposal: WritingProposal;
  onResolved?: (action: "accepted" | "rejected" | "partial") => void;
  className?: string;
};

type ConfirmKind = "accept-all" | "accept-partial" | "reject" | null;

function ReviewCompareSkeleton() {
  return (
    <div
      className="grid gap-4 md:grid-cols-2"
      data-testid="review-compare-skeleton"
      aria-busy="true"
      aria-label="Caricamento confronto"
    >
      {[0, 1].map((col) => (
        <div
          key={col}
          className="space-y-3 rounded-lg border border-border bg-surface p-4"
          style={{ animationDelay: `${col * 80}ms` }}
        >
          <div className="h-4 w-24 animate-pulse rounded bg-surface-muted" />
          <div className="h-16 animate-pulse rounded bg-surface-muted" />
          <div className="h-16 animate-pulse rounded bg-surface-muted [animation-delay:120ms]" />
          <div className="h-12 animate-pulse rounded bg-surface-muted [animation-delay:200ms]" />
        </div>
      ))}
    </div>
  );
}

function HunkBlock({
  hunk,
  side,
  selected,
  onToggle,
}: {
  hunk: ParagraphHunk;
  side: "original" | "proposed";
  selected: boolean;
  onToggle?: () => void;
}) {
  const text = side === "original" ? hunk.original : hunk.proposed;
  if (!text) return null;

  const isChange = hunk.status !== "unchanged";
  const selectable = isChange && side === "proposed" && onToggle;

  const statusClass =
    hunk.status === "added"
      ? "bg-success/10"
      : hunk.status === "removed"
        ? "bg-danger/10 line-through"
        : hunk.status === "modified" && side === "proposed"
          ? "bg-success/10"
          : hunk.status === "modified" && side === "original"
            ? "bg-danger/10 line-through"
            : "";

  const content = (
    <p className={cn("whitespace-pre-wrap text-sm leading-relaxed text-ink", statusClass)}>
      {text}
    </p>
  );

  if (!selectable) {
    return (
      <div className="rounded-md border border-transparent p-2" data-hunk-id={hunk.id}>
        {content}
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={onToggle}
      data-hunk-id={hunk.id}
      aria-pressed={selected}
      className={cn(
        "w-full rounded-md border p-2 text-left transition-colors cursor-pointer",
        selected
          ? "border-accent ring-2 ring-accent bg-accent/5"
          : "border-border hover:border-accent/50"
      )}
    >
      {content}
    </button>
  );
}

/**
 * Side-by-side revision compare with paragraph hunk selection — PX2-EWO-007.
 * Layer: Business (Product Plane)
 */
export function ReviewCompare({
  chapterId,
  proposal,
  onResolved,
  className,
}: ReviewCompareProps) {
  const [chapter, setChapter] = useState<Chapter | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedHunks, setSelectedHunks] = useState<Set<string>>(new Set());
  const [confirmKind, setConfirmKind] = useState<ConfirmKind>(null);
  const [persisting, setPersisting] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    chapterClient
      .get(chapterId)
      .then((ch) => {
        if (!cancelled) setChapter(ch);
      })
      .catch(() => {
        if (!cancelled) setError("Impossibile caricare il capitolo.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [chapterId]);

  const originalContent = chapter?.content_md ?? "";
  const proposedContent = useMemo(
    () => applyProposalToContent(originalContent, proposal),
    [originalContent, proposal]
  );

  const hunks = useMemo(
    () => computeParagraphDiff(originalContent, proposedContent),
    [originalContent, proposedContent]
  );

  const changeHunks = useMemo(() => selectableHunks(hunks), [hunks]);

  const toggleHunk = useCallback((id: string) => {
    setSelectedHunks((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }, []);

  const persistChapter = useCallback(
    async (content: string) => {
      if (!chapter) throw new Error("Capitolo non caricato");
      await chapterClient.update(chapterId, {
        content_md: content,
        expected_version: chapter.version,
      });
    },
    [chapter, chapterId]
  );

  const handleConfirm = async () => {
    if (!confirmKind || !chapter) return;
    setPersisting(true);
    setFeedback(null);

    try {
      if (confirmKind === "reject") {
        await proposalClient.reject(proposal.id);
        setFeedback("Proposta rifiutata — il capitolo non è stato modificato.");
        onResolved?.("rejected");
      } else if (confirmKind === "accept-all") {
        await proposalClient.accept(proposal.id, {
          expected_chapter_version: chapter.version,
        });
        setFeedback("Revisione accettata — bozza del capitolo aggiornata.");
        onResolved?.("accepted");
      } else {
        const merged = mergeAcceptedHunks(hunks, selectedHunks);
        await persistChapter(merged);
        await proposalClient.reject(proposal.id, { reason: "partial_accept" });
        setFeedback("Modifiche parziali accettate — bozza del capitolo aggiornata.");
        onResolved?.("partial");
      }
    } catch {
      setFeedback("Errore durante il salvataggio. Riprova.");
    } finally {
      setPersisting(false);
      setConfirmKind(null);
    }
  };

  if (loading) {
    return (
      <section className={className} aria-labelledby="review-compare-heading">
        <ReviewCompareSkeleton />
      </section>
    );
  }

  if (error || !chapter) {
    return (
      <section className={className}>
        <p className="text-sm text-danger" role="alert">
          {error ?? "Capitolo non disponibile."}
        </p>
      </section>
    );
  }

  const partialDisabled = selectedHunks.size === 0;
  const confirmMessages: Record<Exclude<ConfirmKind, null>, string> = {
    "accept-all":
      "Confermi di accettare tutte le modifiche proposte? La bozza del capitolo verrà aggiornata.",
    "accept-partial":
      "Confermi di accettare i paragrafi selezionati? La bozza del capitolo verrà aggiornata.",
    reject:
      "Confermi di rifiutare questa proposta? Il capitolo non verrà modificato.",
  };

  return (
    <section
      className={className}
      aria-labelledby="review-compare-heading"
      data-testid="review-compare"
    >
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <h2 id="review-compare-heading" className="text-lg font-semibold text-ink">
          {chapter.title}
        </h2>
        <span className="text-xs font-medium text-ink-muted">
          Proposta AI · {proposal.actionLabel}
        </span>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-lg border border-border bg-surface p-4">
          <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-ink-muted">
            Originale
          </h3>
          <div className="space-y-2">
            {hunks.map((hunk) =>
              hunk.original ? (
                <HunkBlock key={`orig-${hunk.id}`} hunk={hunk} side="original" selected={false} />
              ) : null
            )}
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-4">
          <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-accent">
            Proposta
          </h3>
          <div className="space-y-2">
            {hunks.map((hunk) =>
              hunk.proposed ? (
                <HunkBlock
                  key={`prop-${hunk.id}`}
                  hunk={hunk}
                  side="proposed"
                  selected={selectedHunks.has(hunk.id)}
                  onToggle={
                    hunk.status !== "unchanged"
                      ? () => toggleHunk(hunk.id)
                      : undefined
                  }
                />
              ) : null
            )}
          </div>
          {changeHunks.length > 0 ? (
            <p className="mt-3 text-xs text-ink-muted">
              Seleziona i paragrafi da accettare parzialmente.
            </p>
          ) : null}
        </div>
      </div>

      <div
        className="mt-6 flex flex-wrap items-center gap-3 border-t border-border pt-4"
        role="toolbar"
        aria-label="Azioni revisione"
      >
        <button
          type="button"
          onClick={() => setConfirmKind("accept-all")}
          disabled={changeHunks.length === 0 || persisting}
          className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent/90 disabled:cursor-not-allowed disabled:opacity-50 cursor-pointer"
        >
          Accetta tutto
        </button>
        <button
          type="button"
          onClick={() => setConfirmKind("accept-partial")}
          disabled={partialDisabled || persisting}
          className="rounded-md border border-border bg-surface px-4 py-2 text-sm font-medium text-ink hover:bg-surface-muted disabled:cursor-not-allowed disabled:opacity-50 cursor-pointer"
        >
          Accetta parziale
        </button>
        <button
          type="button"
          onClick={() => setConfirmKind("reject")}
          disabled={persisting}
          className="rounded-md border border-danger/30 px-4 py-2 text-sm font-medium text-danger hover:bg-danger/5 disabled:cursor-not-allowed disabled:opacity-50 cursor-pointer"
        >
          Rifiuta
        </button>
        <Link
          href={`/writing/${encodeURIComponent(chapterId)}`}
          className="rounded-md px-4 py-2 text-sm font-medium text-ink-muted hover:text-ink hover:underline cursor-pointer"
        >
          Modifica
        </Link>
      </div>

      {confirmKind ? (
        <div
          className="mt-4 rounded-lg border border-border bg-surface p-4"
          role="dialog"
          aria-labelledby="review-confirm-title"
          data-testid="review-confirm-dialog"
        >
          <h3 id="review-confirm-title" className="text-sm font-semibold text-ink">
            Conferma operazione
          </h3>
          <p className="mt-2 text-sm text-ink-muted">{confirmMessages[confirmKind]}</p>
          <div className="mt-4 flex gap-3">
            <button
              type="button"
              onClick={() => void handleConfirm()}
              disabled={persisting}
              className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent/90 disabled:opacity-50 cursor-pointer"
              data-testid="review-confirm-yes"
            >
              {persisting ? "Salvataggio…" : "Conferma"}
            </button>
            <button
              type="button"
              onClick={() => setConfirmKind(null)}
              disabled={persisting}
              className="rounded-md border border-border px-4 py-2 text-sm font-medium text-ink hover:bg-surface-muted cursor-pointer"
              data-testid="review-confirm-no"
            >
              Annulla
            </button>
          </div>
        </div>
      ) : null}

      {feedback ? (
        <p className="mt-3 text-sm text-ink-muted" role="status">
          {feedback}
        </p>
      ) : null}
    </section>
  );
}
