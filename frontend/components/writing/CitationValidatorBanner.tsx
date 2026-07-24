"use client";

import {
  validateCitations,
  type CitationIssue,
} from "@/lib/citationValidation";

type Props = {
  text: string;
  issues?: CitationIssue[] | null;
  pending?: boolean;
  error?: string | null;
  className?: string;
};

/** Inline citation validator status (PX6-EWO-003). */
export function CitationValidatorBanner({
  text,
  issues,
  pending = false,
  error = null,
  className,
}: Props) {
  if (pending) {
    return (
      <div role="status" className={className}>
        <p className="text-xs text-ink-muted">Verifica citazioni in corso…</p>
      </div>
    );
  }
  if (error) {
    return (
      <div role="alert" className={className}>
        <p className="text-xs text-warning">{error}</p>
      </div>
    );
  }

  const resolvedIssues = issues ?? validateCitations(text);
  const blocking = resolvedIssues.filter((issue) =>
    issue.code === "invalid_numeric" ||
    issue.code === "unlinked_author_date"
  );
  if (blocking.length === 0) return null;

  return (
    <div
      role="status"
      data-testid="citation-validator-banner"
      className={className}
    >
      <ul className="space-y-1 text-xs text-warning">
        {blocking.map((issue) => (
          <li key={`${issue.start}:${issue.matched}`}>
            {issue.code === "unlinked_author_date"
              ? `Citazione non collegata: ${issue.matched}`
              : `${issue.matched} — usa (Autore, Anno)`}
          </li>
        ))}
      </ul>
    </div>
  );
}
