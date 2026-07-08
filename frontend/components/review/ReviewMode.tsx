"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { WritingContextBar } from "@/components/context";
import { contextClient, type ContextPacket } from "@/lib/contextClient";
import { chapterClient, type Chapter } from "@/lib/chapterClient";
import {
  getPendingProposals,
  getPendingProposalsForChapter,
  refreshProposalsFromApi,
  type WritingProposal,
} from "@/lib/proposalQueue";
import { ReviewComparePanel } from "./ReviewComparePanel";
import { ReviewKnowledgePanel } from "./ReviewKnowledgePanel";
import { ReviewDocumentSelector } from "./ReviewDocumentSelector";
import {
  OPEN_REVIEW_EVENT,
  type OpenReviewDetail,
} from "./reviewIntegration";
import {
  ReviewWorkflowSteps,
  type ReviewWorkflowStep,
} from "./ReviewWorkflowSteps";
import type { ReviewChapter } from "./reviewTypes";
import { reviewStatusLabel } from "./reviewTypes";

export type ReviewModeProps = {
  className?: string;
  contextPacket: ContextPacket;
};

function chapterToReviewItem(ch: Chapter, pendingCount: number): ReviewChapter {
  const statusMap: Record<Chapter["status"], ReviewChapter["status"]> = {
    draft: "bozza",
    review: "revisione",
    approved: "approvato",
    published: "approvato",
  };
  return {
    id: ch.id,
    title: ch.title,
    status: statusMap[ch.status] ?? "bozza",
    pendingChanges: pendingCount,
  };
}

/**
 * Review mode shell — full-width compare workspace with ContextBar (PX2-EWO-007).
 * Distinct from /ai power mode (ADR-0039).
 * Layer: Business (Product Plane)
 */
export function ReviewMode({ className, contextPacket }: ReviewModeProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const chapterParam = searchParams.get("chapter");
  const proposalParam = searchParams.get("proposal");

  const [context, setContext] = useState(contextPacket);

  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [loadingChapters, setLoadingChapters] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(chapterParam);
  const [selectedProposalId, setSelectedProposalId] = useState<string | null>(proposalParam);
  const [step, setStep] = useState<ReviewWorkflowStep>("select");
  const [queueVersion, setQueueVersion] = useState(0);

  const refreshQueue = useCallback(() => {
    void refreshProposalsFromApi().then(() => {
      setQueueVersion((v) => v + 1);
    });
  }, []);

  useEffect(() => {
    let cancelled = false;
    refreshProposalsFromApi()
      .then(() => {
        if (!cancelled) setQueueVersion((v) => v + 1);
      })
      .catch(() => {
        if (!cancelled) setQueueVersion((v) => v + 1);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoadingChapters(true);
    chapterClient
      .list()
      .then((list) => {
        if (!cancelled) setChapters(list);
      })
      .catch(() => {
        if (!cancelled) setChapters([]);
      })
      .finally(() => {
        if (!cancelled) setLoadingChapters(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const handler = (event: Event) => {
      const detail = (event as CustomEvent<OpenReviewDetail>).detail;
      const url = detail?.chapterId
        ? `/review?chapter=${encodeURIComponent(detail.chapterId)}`
        : "/review";
      router.push(url);
    };
    window.addEventListener(OPEN_REVIEW_EVENT, handler);
    return () => window.removeEventListener(OPEN_REVIEW_EVENT, handler);
  }, [router]);

  useEffect(() => {
    if (chapterParam) {
      setSelectedId(chapterParam);
      setStep("compare");
    }
    if (proposalParam) setSelectedProposalId(proposalParam);
  }, [chapterParam, proposalParam]);

  useEffect(() => {
    if (!selectedId) {
      setContext(contextPacket);
      return;
    }
    let cancelled = false;
    contextClient
      .get(contextPacket.project_context.project_id, {
        surface: "review",
        entityType: "chapter",
        entityId: selectedId,
      })
      .then((packet) => {
        if (!cancelled) setContext(packet);
      })
      .catch(() => {
        if (!cancelled) setContext(contextPacket);
      });
    return () => {
      cancelled = true;
    };
  }, [selectedId, contextPacket]);

  const pendingProposals = useMemo(() => {
    void queueVersion;
    return getPendingProposals();
  }, [queueVersion]);

  const reviewChapters = useMemo((): ReviewChapter[] => {
    const chapterIdsWithPending = new Set(pendingProposals.map((p) => p.chapterId));
    const fromApi = chapters
      .filter((ch) => chapterIdsWithPending.has(ch.id))
      .map((ch) =>
        chapterToReviewItem(ch, getPendingProposalsForChapter(ch.id).length)
      );

    if (fromApi.length > 0) return fromApi;

    return [...chapterIdsWithPending].map((id) => ({
      id,
      title: `Capitolo ${id}`,
      status: "revisione" as const,
      pendingChanges: getPendingProposalsForChapter(id).length,
    }));
  }, [chapters, pendingProposals]);

  const activeProposal = useMemo((): WritingProposal | null => {
    if (!selectedId) return null;
    const forChapter = getPendingProposalsForChapter(selectedId);
    if (forChapter.length === 0) return null;
    if (selectedProposalId) {
      return forChapter.find((p) => p.id === selectedProposalId) ?? forChapter[0];
    }
    return forChapter[0];
  }, [selectedId, selectedProposalId, queueVersion]);

  function handleSelect(id: string) {
    setSelectedId(id);
    setSelectedProposalId(null);
    setStep("select");
    router.replace(`/review?chapter=${encodeURIComponent(id)}`, { scroll: false });
  }

  function handleCompare() {
    if (!selectedId || !activeProposal) return;
    setStep("compare");
    router.replace(
      `/review?chapter=${encodeURIComponent(selectedId)}&proposal=${encodeURIComponent(activeProposal.id)}`,
      { scroll: false }
    );
  }

  function handleResolved(action: "accepted" | "rejected" | "partial") {
    setStep("accept");
    refreshQueue();
    if (action !== "rejected") {
      setSelectedProposalId(null);
    }
  }

  const showCompare = step === "compare" || step === "accept";
  const hasPending = reviewChapters.length > 0;

  return (
    <div className={["flex flex-col gap-6", className].filter(Boolean).join(" ")}>
      <WritingContextBar packet={context} />

      <div className="px-4 lg:px-6">
        <header className="mb-6">
          <p className="text-xs font-medium uppercase tracking-wide text-ink-muted">
            PX-2 · Revisione
          </p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-ink">
            Revisione
          </h1>
          <p className="mt-2 max-w-prose text-sm leading-relaxed text-ink-muted">
            Confronta le modifiche proposte e accetta o rifiuta con conferma operatore.
            Distinta dalla chat AI in{" "}
            <Link
              href="/ai"
              className="font-medium text-accent underline-offset-2 hover:underline cursor-pointer"
            >
              /ai
            </Link>
            .
          </p>
        </header>

        <ReviewWorkflowSteps current={step} className="mb-8" />

        {!hasPending && !loadingChapters ? (
          <div
            className="rounded-lg border border-dashed border-border bg-surface-muted p-12 text-center"
            data-testid="review-empty-state"
          >
            <p className="text-sm text-ink-muted">Nessuna revisione in sospeso</p>
            <Link
              href="/writing"
              className="mt-4 inline-block rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent/90 cursor-pointer"
            >
              Avvia revisione
            </Link>
          </div>
        ) : (
          <div className="grid gap-8 xl:grid-cols-[minmax(0,16rem)_1fr]">
            <ReviewDocumentSelector
              chapters={reviewChapters}
              selectedId={selectedId}
              onSelect={handleSelect}
            />

            <div className="min-w-0 space-y-6">
              <ReviewKnowledgePanel packet={context} chapterId={selectedId} />

              {selectedId && step === "select" && activeProposal ? (
                <div>
                  <button
                    type="button"
                    onClick={handleCompare}
                    className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent/90 cursor-pointer"
                  >
                    Confronta revisione
                  </button>
                </div>
              ) : null}

              {showCompare ? (
                <ReviewComparePanel
                  chapterId={selectedId}
                  proposal={activeProposal}
                  onResolved={handleResolved}
                />
              ) : (
                <ReviewComparePanel chapterId={null} proposal={null} />
              )}

              {activeProposal && step === "select" ? (
                <p className="text-xs text-ink-muted">
                  {reviewStatusLabel("revisione")} · {activeProposal.actionLabel}
                </p>
              ) : null}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export { dispatchOpenReview } from "./reviewIntegration";
