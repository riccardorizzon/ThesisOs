"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { ReviewActionBar } from "./ReviewActionBar";
import { ReviewComparePanel } from "./ReviewComparePanel";
import { ReviewDocumentSelector } from "./ReviewDocumentSelector";
import { REVIEW_CHAPTERS } from "./reviewStub";
import {
  ReviewWorkflowSteps,
  type ReviewWorkflowStep,
} from "./ReviewWorkflowSteps";

export type ReviewModeProps = {
  className?: string;
};

/**
 * Review mode shell — revision workflow distinct from /ai power mode (ADR-0039).
 * Workflow: select → compare → accept.
 * Layer: Business (Product Plane)
 */
export function ReviewMode({ className }: ReviewModeProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [step, setStep] = useState<ReviewWorkflowStep>("select");
  const [feedback, setFeedback] = useState<string | null>(null);

  const selectedChapter = useMemo(
    () => REVIEW_CHAPTERS.find((c) => c.id === selectedId) ?? null,
    [selectedId]
  );

  function handleSelect(id: string) {
    setSelectedId(id);
    setStep("select");
    setFeedback(null);
  }

  function handleCompare() {
    if (!selectedChapter) return;
    setStep("compare");
    setFeedback(null);
  }

  function handleAccept() {
    if (!selectedChapter) return;
    setStep("accept");
    setFeedback(
      `Revisione accettata per «${selectedChapter.title}» (stub — esecuzione PX-2+).`
    );
  }

  function handleReject() {
    if (!selectedChapter) return;
    setStep("accept");
    setFeedback(
      `Revisione rifiutata per «${selectedChapter.title}» (stub — esecuzione PX-2+).`
    );
  }

  const actionsEnabled = step === "compare" || step === "accept";

  return (
    <div className={["mx-auto max-w-5xl", className].filter(Boolean).join(" ")}>
      <header className="mb-8">
        <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
          PX-1 · Revisione
        </p>
        <h1 className="mt-1 text-2xl font-semibold tracking-tight text-gray-900">
          Revisione
        </h1>
        <p className="mt-2 max-w-prose text-sm leading-relaxed text-gray-600">
          Modalità revisione strutturata: seleziona un capitolo, confronta le
          modifiche proposte e accetta o rifiuta. Distinta dalla chat AI in{" "}
          <Link
            href="/ai"
            className="font-medium text-blue-800 underline-offset-2 hover:underline cursor-pointer"
          >
            /ai
          </Link>
          .
        </p>
      </header>

      <ReviewWorkflowSteps current={step} className="mb-8" />

      <div className="grid gap-8 lg:grid-cols-[minmax(0,16rem)_1fr]">
        <ReviewDocumentSelector
          chapters={REVIEW_CHAPTERS}
          selectedId={selectedId}
          onSelect={handleSelect}
        />

        <div className="space-y-6">
          <ReviewComparePanel chapter={selectedChapter} />

          {selectedChapter && step === "select" ? (
            <div>
              <button
                type="button"
                onClick={handleCompare}
                className="rounded-md bg-blue-800 px-4 py-2 text-sm font-medium text-white hover:bg-blue-900 cursor-pointer"
              >
                Confronta revisione
              </button>
            </div>
          ) : null}

          <ReviewActionBar
            enabled={actionsEnabled}
            onAccept={handleAccept}
            onReject={handleReject}
            feedback={feedback}
          />
        </div>
      </div>
    </div>
  );
}
