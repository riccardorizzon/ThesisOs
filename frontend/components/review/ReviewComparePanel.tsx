"use client";

import type { ReviewChapter } from "./reviewStub";

export type ReviewComparePanelProps = {
  chapter: ReviewChapter | null;
  className?: string;
};

/**
 * Diff/compare placeholder — side-by-side revision preview stub.
 * Layer: Business (Product Plane)
 */
export function ReviewComparePanel({ chapter, className }: ReviewComparePanelProps) {
  if (!chapter) {
    return (
      <section
        aria-labelledby="review-compare-heading"
        className={className}
      >
        <h2
          id="review-compare-heading"
          className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-500"
        >
          Confronto revisioni
        </h2>
        <div className="rounded-lg border border-dashed border-gray-300 bg-gray-50 p-8 text-center">
          <p className="text-sm text-gray-500">
            Seleziona un capitolo per visualizzare il confronto bozza / revisione.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section
      aria-labelledby="review-compare-heading"
      className={className}
    >
      <h2
        id="review-compare-heading"
        className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-500"
      >
        Confronto revisioni
      </h2>
      <p className="mb-4 text-sm text-gray-600">
        {chapter.title} — anteprima differenze (stub PX-1)
      </p>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
            Versione corrente
          </h3>
          <p className="font-mono text-sm leading-relaxed text-gray-700">
            La moda contemporanea riflette tensioni tra artigianalità e
            riproducibilità industriale.
          </p>
        </div>
        <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-blue-800">
            Revisione proposta
          </h3>
          <p className="font-mono text-sm leading-relaxed text-gray-800">
            <span className="bg-green-100 text-green-900">
              La moda contemporanea articola
            </span>{" "}
            tensioni tra artigianalità e riproducibilità{" "}
            <span className="line-through text-gray-400">industriale</span>{" "}
            <span className="bg-green-100 text-green-900">di massa</span>.
          </p>
        </div>
      </div>
    </section>
  );
}
