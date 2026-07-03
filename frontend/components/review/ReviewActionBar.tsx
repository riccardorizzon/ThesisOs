"use client";

export type ReviewActionBarProps = {
  enabled: boolean;
  onAccept: () => void;
  onReject: () => void;
  feedback?: string | null;
  className?: string;
};

/**
 * Accept/reject action stubs for revision workflow.
 * Layer: Business (Product Plane)
 */
export function ReviewActionBar({
  enabled,
  onAccept,
  onReject,
  feedback,
  className,
}: ReviewActionBarProps) {
  return (
    <section
      aria-labelledby="review-actions-heading"
      className={className}
    >
      <h2
        id="review-actions-heading"
        className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-500"
      >
        Decisione revisione
      </h2>
      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          disabled={!enabled}
          onClick={onAccept}
          className={[
            "rounded-md px-4 py-2 text-sm font-medium transition-colors cursor-pointer",
            enabled
              ? "bg-green-700 text-white hover:bg-green-800"
              : "cursor-not-allowed bg-gray-200 text-gray-400",
          ].join(" ")}
        >
          Accetta revisione
        </button>
        <button
          type="button"
          disabled={!enabled}
          onClick={onReject}
          className={[
            "rounded-md border px-4 py-2 text-sm font-medium transition-colors cursor-pointer",
            enabled
              ? "border-red-700 text-red-700 hover:bg-red-50"
              : "cursor-not-allowed border-gray-200 text-gray-400",
          ].join(" ")}
        >
          Rifiuta
        </button>
      </div>
      {feedback ? (
        <p
          role="status"
          className="mt-3 text-sm text-gray-600"
        >
          {feedback}
        </p>
      ) : !enabled ? (
        <p className="mt-3 text-sm text-gray-500">
          Completa il confronto per abilitare accettazione o rifiuto.
        </p>
      ) : null}
    </section>
  );
}
