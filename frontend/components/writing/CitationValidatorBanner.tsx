"use client";

import { countInvalidNumericCitations } from "@/lib/citationValidation";

type Props = {
  text: string;
  className?: string;
};

/** Inline citation validator status (PX6-EWO-003). */
export function CitationValidatorBanner({ text, className }: Props) {
  const count = countInvalidNumericCitations(text);
  if (count === 0) return null;

  return (
    <div
      role="status"
      data-testid="citation-validator-banner"
      className={className}
    >
      <p className="text-xs text-warning">
        {count === 1
          ? "1 citazione da verificare — usa (Autore, Anno)"
          : `${count} citazioni da verificare — usa (Autore, Anno)`}
      </p>
    </div>
  );
}
